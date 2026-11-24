#!/usr/bin/env python3
"""Colector de metricas SQA CI para The Blog (Equipo M6 - PACS).

Extrae resultados de Surefire XML por categoria (@Tag), cobertura JaCoCo XML,
subcaracteristicas ISO/IEC 25010 de Adecuacion Funcional, y gestiona el historial
JSON para el Monitor Web en Tiempo Real y Google Sheets.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any


ISO_SUBCHARACTERISTICS = ("completitud", "correccion", "pertinencia")
CATEGORIES = ("unitaria", "integracion", "categoria")
MAX_HISTORY_RUNS = 50
MIN_HEALTHY_LINE_COVERAGE_PCT = 30.0


def parse_testsuite_xml(path: str) -> dict[str, Any]:
    """Parsea un archivo TEST-*.xml de Maven Surefire."""
    root = ET.parse(path).getroot()
    total = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))
    passed = max(0, total - failures - errors - skipped)

    testcases = []
    for tc in root.findall("testcase"):
        tc_name = tc.attrib.get("name", "")
        tc_status = "passed"
        if tc.find("failure") is not None:
            tc_status = "failed"
        elif tc.find("error") is not None:
            tc_status = "error"
        elif tc.find("skipped") is not None:
            tc_status = "skipped"
        testcases.append({
            "name": tc_name,
            "classname": tc.attrib.get("classname", ""),
            "time_sec": float(tc.attrib.get("time", 0.0)),
            "status": tc_status,
        })

    return {
        "suite": root.attrib.get("name", os.path.basename(path)),
        "tests": total,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time_sec": round(float(root.attrib.get("time", 0.0)), 3),
        "testcases": testcases,
    }


def classify_suite_name(suite_name: str) -> str:
    """Clasifica una suite por convencion de paquete/nombre cuando no hay carpeta dedicada."""
    lower = suite_name.lower()
    if "integration" in lower or "integracion" in lower:
        return "integracion"
    if "category" in lower or "categoria" in lower or "adecuacionfuncional" in lower:
        return "categoria"
    return "unitaria"


def aggregate_suites(suites: list[dict[str, Any]]) -> dict[str, int]:
    """Suma totales de ejecucion sobre una lista de suites parseadas."""
    totals = {"total": 0, "passed": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        totals["total"] += suite["tests"]
        totals["passed"] += suite["passed"]
        totals["failures"] += suite["failures"]
        totals["errors"] += suite["errors"]
        totals["skipped"] += suite["skipped"]
    return totals


def collect_category_metrics(backend_dir: str, fallback_suites: list[dict[str, Any]]) -> tuple[dict[str, dict[str, int]], list[dict[str, Any]]]:
    """Lee reportes por categoria desde target/sqa-reports/<cat> o usa clasificacion fallback."""
    sqa_root = os.path.join(backend_dir, "target", "sqa-reports")
    parsed_by_cat: dict[str, list[dict[str, Any]]] = {cat: [] for cat in CATEGORIES}
    used_dedicated = False

    for cat in CATEGORIES:
        pattern = os.path.join(sqa_root, cat, "TEST-*.xml")
        files = sorted(glob.glob(pattern))
        if files:
            used_dedicated = True
            for path in files:
                try:
                    parsed_by_cat[cat].append(parse_testsuite_xml(path))
                except Exception as exc:
                    print(f"Aviso leyendo {path}: {exc}", file=sys.stderr)

    if not used_dedicated:
        for suite in fallback_suites:
            cat = classify_suite_name(suite["suite"])
            parsed_by_cat[cat].append(suite)

    summary = {cat: aggregate_suites(parsed_by_cat[cat]) for cat in CATEGORIES}
    return summary, parsed_by_cat["categoria"]


def collect_iso_breakdown(categoria_suites: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Extrae metricas por subcaracteristica ISO/IEC 25010 desde los casos de @Tag('categoria')."""
    breakdown = {
        sub: {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        for sub in ISO_SUBCHARACTERISTICS
    }
    for suite in categoria_suites:
        for tc in suite.get("testcases", []):
            name_lower = tc.get("name", "").lower()
            matched = [sub for sub in ISO_SUBCHARACTERISTICS if sub in name_lower]
            for sub in matched:
                breakdown[sub]["total"] += 1
                status = tc.get("status")
                if status == "passed":
                    breakdown[sub]["passed"] += 1
                elif status == "skipped":
                    breakdown[sub]["skipped"] += 1
                else:
                    breakdown[sub]["failed"] += 1
    return breakdown


def collect_jacoco_metrics(jacoco_path: str) -> dict[str, Any]:
    """Parsea los contadores globales del XML generado por JaCoCo."""
    counters: dict[str, dict[str, Any]] = {}
    if not os.path.exists(jacoco_path):
        return counters

    root = ET.parse(jacoco_path).getroot()
    for counter in root.findall("./counter"):
        ctype = counter.attrib.get("type")
        if not ctype:
            continue
        missed = int(counter.attrib.get("missed", 0))
        covered = int(counter.attrib.get("covered", 0))
        total = missed + covered
        pct = round((covered / total) * 100, 2) if total > 0 else 0.0
        counters[ctype] = {
            "covered": covered,
            "missed": missed,
            "total": total,
            "pct": pct,
        }
    return counters


def compute_quality_gate(
    tests_total: int,
    tests_failures: int,
    tests_errors: int,
    tests_skipped: int,
    line_coverage_pct: float | None,
    backend_status: str,
    frontend_status: str,
) -> str:
    """Calcula el semaforo SQA (VERDE, AMARILLO, ROJO) con reglas deterministas."""
    failed_states = {"failure", "cancelled", "timed_out"}
    if (
        tests_total == 0
        or tests_failures > 0
        or tests_errors > 0
        or backend_status in failed_states
        or frontend_status in failed_states
    ):
        return "ROJO"

    if (
        tests_skipped > 0
        or (line_coverage_pct is not None and line_coverage_pct < MIN_HEALTHY_LINE_COVERAGE_PCT)
        or (backend_status not in ("success", "local", "") or frontend_status not in ("success", "local", ""))
    ):
        return "AMARILLO"

    return "VERDE"


def enrich_with_statuses(
    metrics: dict[str, Any],
    backend_status: str,
    frontend_status: str,
) -> dict[str, Any]:
    """Actualiza estados de jobs CI y recalcula el semaforo de calidad."""
    metrics["backend_status"] = backend_status
    metrics["frontend_status"] = frontend_status
    metrics["quality_gate"] = compute_quality_gate(
        tests_total=int(metrics.get("tests_total", 0)),
        tests_failures=int(metrics.get("tests_failures", 0)),
        tests_errors=int(metrics.get("tests_errors", 0)),
        tests_skipped=int(metrics.get("tests_skipped", 0)),
        line_coverage_pct=metrics.get("line_coverage_pct"),
        backend_status=backend_status,
        frontend_status=frontend_status,
    )
    return metrics


def build_metrics(backend_dir: str, backend_status: str, frontend_status: str) -> dict[str, Any]:
    """Construye el payload canonico de metricas a partir de target/."""
    surefire_pattern = os.path.join(backend_dir, "target", "surefire-reports", "TEST-*.xml")
    surefire_suites: list[dict[str, Any]] = []
    for path in sorted(glob.glob(surefire_pattern)):
        try:
            surefire_suites.append(parse_testsuite_xml(path))
        except Exception as exc:
            print(f"Aviso leyendo {path}: {exc}", file=sys.stderr)

    by_category, categoria_suites = collect_category_metrics(backend_dir, surefire_suites)
    iso_breakdown = collect_iso_breakdown(categoria_suites)

    if surefire_suites:
        overall = aggregate_suites(surefire_suites)
        public_suites = [
            {k: v for k, v in s.items() if k != "testcases"}
            for s in surefire_suites
        ]
    else:
        overall = {
            key: sum(by_category[cat][key] for cat in CATEGORIES)
            for key in ("total", "passed", "failures", "errors", "skipped")
        }
        public_suites = []

    jacoco_path = os.path.join(backend_dir, "target", "site", "jacoco", "jacoco.xml")
    jacoco_counters = collect_jacoco_metrics(jacoco_path)
    line_cov = jacoco_counters.get("LINE", {}).get("pct")
    branch_cov = jacoco_counters.get("BRANCH", {}).get("pct")
    instruction_cov = jacoco_counters.get("INSTRUCTION", {}).get("pct")
    method_cov = jacoco_counters.get("METHOD", {}).get("pct")
    class_cov = jacoco_counters.get("CLASS", {}).get("pct")

    total = overall["total"]
    passed = overall["passed"]
    pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0

    commit_sha = os.environ.get("GITHUB_SHA", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "PanzerOg/Blog-Equipo-M6-PACS")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else ""

    raw_msg = (os.environ.get("GITHUB_COMMIT_MESSAGE") or "").strip()
    commit_message = raw_msg.splitlines()[0][:180] if raw_msg else "Ejecucion CI / Local"

    metrics: dict[str, Any] = {
        "schema_version": "1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": commit_sha,
        "commit_short": commit_sha[:7] if commit_sha else "local",
        "commit_message": commit_message,
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "run_id": run_id,
        "run_number": int(run_number) if str(run_number).isdigit() else None,
        "run_url": run_url,
        "tests_total": total,
        "tests_passed": passed,
        "tests_failures": overall["failures"],
        "tests_errors": overall["errors"],
        "tests_skipped": overall["skipped"],
        "pass_rate_pct": pass_rate,
        "by_category": by_category,
        "iso_25010_adecuacion_funcional": iso_breakdown,
        "line_coverage_pct": line_cov,
        "branch_coverage_pct": branch_cov,
        "instruction_coverage_pct": instruction_cov,
        "method_coverage_pct": method_cov,
        "class_coverage_pct": class_cov,
        "jacoco": jacoco_counters,
        "suites": public_suites,
    }
    return enrich_with_statuses(metrics, backend_status, frontend_status)


def write_step_summary(metrics: dict[str, Any]) -> None:
    """Agrega una tabla resumen al GITHUB_STEP_SUMMARY cuando esta disponible."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    by_cat = metrics["by_category"]
    iso = metrics["iso_25010_adecuacion_funcional"]
    line_cov = metrics.get("line_coverage_pct")
    branch_cov = metrics.get("branch_coverage_pct")

    with open(summary_file, "a", encoding="utf-8") as sf:
        sf.write("## Resumen SQA CI - Backend (Spring Boot + JUnit 5 + JaCoCo)\n\n")
        sf.write(f"- **Commit:** `{metrics['commit_short']}` ({metrics['branch']})\n")
        sf.write(
            f"- **Pruebas Totales:** {metrics['tests_total']} | "
            f"**Aprobadas:** {metrics['tests_passed']} ({metrics['pass_rate_pct']}%) | "
            f"**Fallos:** {metrics['tests_failures']} | "
            f"**Errores:** {metrics['tests_errors']} | "
            f"**Omitidas:** {metrics['tests_skipped']}\n"
        )
        sf.write(
            f"- **Por Categoria:** Unitarias `{by_cat['unitaria']['passed']}/{by_cat['unitaria']['total']}` | "
            f"Integracion `{by_cat['integracion']['passed']}/{by_cat['integracion']['total']}` | "
            f"Categoria ISO 25010 `{by_cat['categoria']['passed']}/{by_cat['categoria']['total']}`\n"
        )
        sf.write(
            f"- **Adecuacion Funcional (ISO/IEC 25010):** "
            f"Completitud `{iso['completitud']['passed']}/{iso['completitud']['total']}` | "
            f"Correccion `{iso['correccion']['passed']}/{iso['correccion']['total']}` | "
            f"Pertinencia `{iso['pertinencia']['passed']}/{iso['pertinencia']['total']}`\n"
        )
        sf.write(f"- **Cobertura Lineas (JaCoCo):** {line_cov if line_cov is not None else 'N/D'}%\n")
        sf.write(f"- **Cobertura Ramas (JaCoCo):** {branch_cov if branch_cov is not None else 'N/D'}%\n")
        sf.write(f"- **Semaforo SQA:** `{metrics['quality_gate']}`\n\n")

        suites = metrics.get("suites", [])
        if suites:
            sf.write("| Suite | Total | Fallos | Errores | Omitidas | Tiempo (s) |\n")
            sf.write("| :--- | ---: | ---: | ---: | ---: | ---: |\n")
            for s in suites:
                sf.write(
                    f"| `{s['suite']}` | {s['tests']} | {s['failures']} | "
                    f"{s['errors']} | {s['skipped']} | {s['time_sec']} |\n"
                )


def load_json(path: str, default: Any) -> Any:
    """Carga un archivo JSON si existe y es valido; caso contrario devuelve default."""
    if not path or not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: str, data: Any) -> None:
    """Escribe un archivo JSON asegurando la creacion de sus carpetas padre."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def update_history(input_path: str, history_path: str, latest_output: str | None) -> dict[str, Any]:
    """Agrega o actualiza una corrida en metrics-history.json manteniendo hasta 50 registros."""
    new_run = load_json(input_path, None)
    if not isinstance(new_run, dict):
        raise ValueError(f"No se pudo leer un objeto JSON valido en {input_path}")

    history = load_json(history_path, {"project": "The Blog - Equipo M6 SQA", "runs": []})
    runs: list[dict[str, Any]] = history.get("runs", [])
    if not isinstance(runs, list):
        runs = []

    new_key = str(new_run.get("run_id") or "").strip() or str(new_run.get("commit_sha") or "").strip()
    deduped = []
    for existing in runs:
        existing_key = str(existing.get("run_id") or "").strip() or str(existing.get("commit_sha") or "").strip()
        if new_key and existing_key == new_key:
            continue
        deduped.append(existing)

    deduped.append(new_run)
    deduped.sort(key=lambda item: str(item.get("timestamp_utc") or ""))
    if len(deduped) > MAX_HISTORY_RUNS:
        deduped = deduped[-MAX_HISTORY_RUNS:]

    updated_history = {
        "schema_version": "1.0",
        "project": "The Blog - Equipo M6 SQA (ISO/IEC 25010 - Adecuacion Funcional)",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_runs": len(deduped),
        "runs": deduped,
    }
    write_json(history_path, updated_history)
    if latest_output:
        write_json(latest_output, new_run)
    return updated_history


def parse_args() -> argparse.Namespace:
    """Define los argumentos CLI del colector."""
    parser = argparse.ArgumentParser(description="Colector de metricas SQA CI para The Blog")
    parser.add_argument("--backend-dir", default="backend", help="Ruta al directorio backend/")
    parser.add_argument("--output", help="Ruta de salida para sqa-ci-metrics.json")
    parser.add_argument("--input", help="JSON existente de metricas para enriquecer o archivar en historial")
    parser.add_argument("--backend-status", default="local", help="Estado del job backend en CI")
    parser.add_argument("--frontend-status", default="local", help="Estado del job frontend en CI")
    parser.add_argument("--write-summary", action="store_true", help="Anexar resumen Markdown a GITHUB_STEP_SUMMARY")
    parser.add_argument("--append-history", help="Ruta a metrics-history.json para agregar el run de --input")
    parser.add_argument("--latest-output", help="Ruta opcional para guardar latest-metrics.json junto al historial")
    return parser.parse_args()


def main() -> int:
    """Punto de entrada del script."""
    args = parse_args()

    if args.input and not args.append_history:
        metrics = load_json(args.input, None)
        if not isinstance(metrics, dict):
            print(f"Error: {args.input} no contiene un objeto JSON valido.", file=sys.stderr)
            return 1
        enrich_with_statuses(metrics, args.backend_status, args.frontend_status)
        target_out = args.output or args.input
        write_json(target_out, metrics)
        print(f"Metricas enriquecidas en {target_out} (quality_gate={metrics['quality_gate']})")
        return 0

    if args.append_history:
        if not args.input:
            print("Error: --append-history requiere --input.", file=sys.stderr)
            return 1
        if args.backend_status != "local" or args.frontend_status != "local":
            metrics = load_json(args.input, None)
            if isinstance(metrics, dict):
                enrich_with_statuses(metrics, args.backend_status, args.frontend_status)
                write_json(args.input, metrics)
        history = update_history(args.input, args.append_history, args.latest_output)
        print(f"Historial actualizado en {args.append_history} ({history['total_runs']} corridas)")
        return 0

    metrics = build_metrics(args.backend_dir, args.backend_status, args.frontend_status)
    output_path = args.output or os.path.join(args.backend_dir, "target", "sqa-ci-metrics.json")
    write_json(output_path, metrics)
    if args.write_summary:
        write_step_summary(metrics)

    print(
        f"Metricas SQA generadas en {output_path}: "
        f"{metrics['tests_passed']}/{metrics['tests_total']} pruebas "
        f"({metrics['pass_rate_pct']}%), JaCoCo Lineas={metrics.get('line_coverage_pct')}%, "
        f"Gate={metrics['quality_gate']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
