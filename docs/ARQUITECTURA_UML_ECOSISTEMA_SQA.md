# Arquitectura UML del Ecosistema Tecnológico y Agéntico SQA

| Metadato ISO/IEC/IEEE 15289 | Valor |
| :--- | :--- |
| **Proyecto** | Aseguramiento de la Calidad del Software (UCAB 2026-2) — Equipo M6 |
| **Sistema Bajo Evaluación (SUT)** | *The Blog* (`PanzerOg/Blog-Equipo-M6-PACS`) — Java 17 / Spring Boot 3.5.6 + Vue 3 |
| **Característica Focal (ISO/IEC 25010)** | Adecuación Funcional (*Completitud, Corrección y Pertinencia Funcional*) |
| **Autor / Rol Responsable** | José Alejandro Montes de Oca Tineo — Líder Tecnológico / DevOp |
| **Estándares de Referencia** | ISO/IEC/IEEE 42010 (Arquitectura), ISO/IEC 25010, ISO/IEC 25059, ISO/IEC/IEEE 29119, ISO/IEC/IEEE 15289 |
| **Trazabilidad Jira / Confluence** | Epic / Tarea DevOp `KAN-69` · Confluence Hub ID `6717610` |
| **Versión / Estado** | v1.0 — Implementado y Verificado en Producción (`main` + `gh-pages` + Sheets) |

---

## 1. Propósito Arquitectónico

Este documento describe la arquitectura integrada del ecosistema tecnológico SQA del Equipo M6, mostrando cómo se articulan los **5 roles humanos**, los **agentes de IA gobernados** (`Antigravity` + `AGENTS.md` + 4 skills especializados), el **servidor MCP oficial de Atlassian**, el **pipeline CI/CD en GitHub Actions** y los **monitores automáticos en tiempo real** (**Google Sheets** y **GitHub Pages**), asistiendo directamente los 6 procesos de gestión SQA especificados en la Sección 13 del proyecto (*Planificación, Ejecución, Dirección, Monitoreo, Control y Evaluación*).

---

## 2. Diagrama 1 — Arquitectura de Componentes (Capa Humana, Agéntica, MCP, CI/CD y Monitor)

```mermaid
flowchart TB
  subgraph HUM["Capa Humana - 5 Lideres Equipo M6"]
    LG["Gabriel Lopez - Lider General"]
    LF["Andres Cardozo - Tester Dinamico"]
    LM["Nahomi Abella - Lider de Metricas"]
    EA["Rebeca Lopez - Escriba Auditora"]
    DV["Jose Montes de Oca - DevOp"]
  end

  subgraph AGT["Capa Agentica Gobernada - Antigravity IDE"]
    AG["AGENTS.md - Aislamiento JSON y Cero Alucinacion"]
    SK_T["Skill sqa-tester-dinamico"]
    SK_E["Skill sqa-escriba-auditor"]
    SK_M["Skill sqa-metricas-monitor"]
    SK_G["Skill sqa-lider-general"]
    SUT["SUT The Blog - backend Spring Boot y frontend Vue 3"]
  end

  subgraph INT["Capa de Integracion y Trazabilidad"]
    MCP["Atlassian MCP - mcp.atlassian.com - 26 tools"]
    TWG["TWG CLI v1.4.6 - Atlassian OAuth"]
    GIT["Repositorio GitHub - PanzerOg/Blog-Equipo-M6-PACS"]
  end

  subgraph CI["Capa CI/CD - GitHub Actions Ubuntu Runner"]
    J_BE["Job backend-pruebas-sqa - Unitaria Integracion Categoria JaCoCo"]
    J_FE["Job frontend-validacion - npm ci build lint"]
    PY["Colector scripts/collect_ci_metrics.py"]
    J_MON["Job publicar-monitor-vivo - Consolidacion y Semaforo SQA"]
    J_DIS["Job notificar-discord - Embed Enriquecido"]
  end

  subgraph MON["Capa de Gestion y Monitor en Tiempo Real"]
    JIRA["Jira Cloud - Tablero KAN y Defectos KAN-60..69"]
    CONF["Confluence Cloud - Hub Ecosistema 6717610"]
    GS["Google Apps Script Webhook - SqaRealtimeWebhook.gs"]
    SH["Google Sheets - Datos_CI_TiempoReal y MONITOR_DINAMICO_TIEMPO_REAL"]
    GHP["Monitor Web en Vivo - Rama gh-pages con Chart.js"]
    DISC["Discord Canal SQA - SQA CI/CD Bot"]
  end

  LG --> SK_G
  LF --> SK_T
  LM --> SK_M
  EA --> SK_E
  DV --> AG

  SK_G & SK_T & SK_M & SK_E --> AG
  AG --> SUT
  SK_G & SK_T & SK_M & SK_E --> MCP
  DV --> TWG
  MCP --> JIRA
  MCP --> CONF
  TWG --> JIRA

  SUT --> GIT
  GIT --> J_BE
  GIT --> J_FE
  J_BE --> PY
  PY --> J_MON
  J_FE --> J_MON
  J_MON --> J_DIS

  J_MON --> GS
  GS --> SH
  J_MON --> GHP
  J_DIS --> DISC
  JIRA -. "Jira Cloud for Sheets" .-> SH
```

---

## 3. Diagrama 2 — Secuencia End-to-End (Del Diseño Asistido por IA al Monitor en Tiempo Real)

```mermaid
sequenceDiagram
  autonumber
  actor Tester as Lider Funcional / Tester
  participant Agente as Antigravity + Skill
  participant MCP as Atlassian MCP
  participant Local as Maven Wrapper Local
  participant Git as GitHub main
  participant CI as GitHub Actions
  participant Py as collect_ci_metrics.py
  participant GS as Google Sheets Webhook
  participant Pages as GitHub Pages gh-pages
  participant Disc as Discord Webhook

  Tester->>Agente: Solicita casos JUnit 5 segun KAN-60..67
  Agente->>MCP: Lee defectos e incidencias en Jira KAN y Confluence
  MCP-->>Agente: Contexto real verificado del SUT
  Agente-->>Tester: Propuesta casos + Tabla Validacion Pertinencia Humana
  Tester->>Local: Ejecuta ./mvnw.cmd test por @Tag y jacoco:report
  Local-->>Tester: 100% pass en perfil test aislado (sin tocar backend/data)
  Tester->>Git: git commit -m "KAN-XX ..." && git push origin main
  Git->>CI: Dispara workflow ci-sqa.yml (branches-ignore gh-pages)

  par Validacion Backend y Frontend
    CI->>CI: Backend ejecuta @Tag unitaria, integracion, categoria y JaCoCo
    CI->>Py: Genera sqa-ci-metrics.json + GITHUB_STEP_SUMMARY
    CI->>CI: Frontend ejecuta npm ci, npm run build y lint diagnostico
  end

  CI->>Py: Consolida estado jobs y calcula Semaforo SQA (VERDE/AMARILLO/ROJO)
  CI->>GS: POST JSON (curl -fsSL) a SqaRealtimeWebhook.gs
  GS-->>CI: Upsert en Datos_CI_TiempoReal + recalcula MONITOR_DINAMICO_TIEMPO_REAL
  CI->>Pages: Actualiza index.html, latest-metrics.json y metrics-history.json
  CI->>Disc: Envia embed con Semaforo, Unit/Int/Cat, Pass Rate y JaCoCo
```

---

## 4. Diagrama 3 — Diagrama de Despliegue e Infraestructura Distribuida

```mermaid
flowchart LR
  subgraph WS["Estacion Local Windows 11 - Lideres del Equipo"]
    IDE["Antigravity IDE + MCP Client"]
    JDK["JDK + mvnw.cmd - byte-buddy-agent"]
    TWG_L["twg CLI v1.4.6"]
    REPO_L["Working Copy Git + backend/target/test-data"]
  end

  subgraph GH["GitHub Cloud - PanzerOg/Blog-Equipo-M6-PACS"]
    ACT["Runner ubuntu-latest - JDK 17 Temurin + Node 20 + Python 3"]
    ART["Artifacts - sqa-backend-reports y sqa-final-metrics"]
    PAGES["GitHub Pages CDN - Branch gh-pages"]
  end

  subgraph ATL["Atlassian Cloud - sqa-team-m6.atlassian.net"]
    MCP_S["Endpoint MCP - mcp.atlassian.com/v2/mcp"]
    J_C["Jira Project KAN y Confluence Space SQA"]
  end

  subgraph GCP["Google Workspace Cloud"]
    APPS["Google Apps Script Web App - doPost / doGet"]
    SHEET["Spreadsheet PACS-SQA-Dashboard-Metricas-KAN"]
  end

  subgraph COM["Comunicacion en Tiempo Real"]
    DIS_S["Discord Webhook API"]
  end

  IDE -- "HTTPS OAuth2" --> MCP_S
  TWG_L -- "GraphQL OAuth2" --> J_C
  MCP_S --> J_C
  REPO_L -- "git push HTTPS" --> ACT
  ACT --> ART
  ACT -- "git push gh-pages" --> PAGES
  ACT -- "HTTPS JSON Redirect" --> APPS
  APPS -- "LockService + SpreadsheetApp" --> SHEET
  ACT -- "HTTPS JSON POST" --> DIS_S
```

---

## 5. Diagrama 4 — Modelo de Clases de Gobernanza, Taxonomía de Pruebas y Telemetría

```mermaid
classDiagram
  class GobernanzaAgentsMd {
    +String sistema = "The Blog"
    +String foco = "ISO/IEC 25010 Adecuacion Funcional"
    +prohibirLecturaEscrituraDatosProd()
    +exigirAislamientoTestProfileOTempDir()
    +exigirTrazabilidadKAN()
    +aplicarProtocoloAntiAlucinacion()
  }

  class SkillRol {
    +String nombre
    +String responsableHumano
    +String[] herramientasPermitidas
    +ejecutarFlujoGuiado()
    +generarTablaPertinenciaHumana()
  }

  class SuiteJUnit5 {
    +String nombreSuite
    +String tagPrincipal
    +String[] subTagsISO25010
    +int total
    +int passed
    +int failures
    +int errors
  }

  class ColectorMetricasCI {
    +int MAX_HISTORY_RUNS = 50
    +float MIN_LINE_COVERAGE = 30.0
    +collect_category_metrics()
    +collect_iso_breakdown()
    +collect_jacoco_metrics()
    +compute_quality_gate()
    +update_history()
  }

  class QualityGate {
    <<enumeration>>
    VERDE
    AMARILLO
    ROJO
  }

  class MonitorTiempoReal {
    +String googleSheetId = "1J43xxO0...19mVU"
    +String ghPagesUrl = "panzerog.github.io/Blog-Equipo-M6-PACS"
    +actualizarGoogleSheets(payload)
    +publicarDashboardWeb(history)
    +notificarDiscord(embed)
  }

  GobernanzaAgentsMd "1" *-- "4" SkillRol : "rige a"
  SkillRol ..> SuiteJUnit5 : "propone bajo arbitraje humano"
  SuiteJUnit5 "1..*" --> "1" ColectorMetricasCI : "alimenta Surefire XML"
  ColectorMetricasCI --> QualityGate : "calcula"
  ColectorMetricasCI --> MonitorTiempoReal : "emite payload JSON"
```

---

## 6. Matriz de Articulación con los 6 Procesos de Gestión SQA (Sección 13)

| Proceso de Gestión (Sección 13) | Responsable Principal | Mecanismo Tecnológico y Agéntico (DevOp) | Evidencia Automática en Tiempo Real |
| :--- | :--- | :--- | :--- |
| **1. Planificación** | Gabriel López (*Líder General*) | `sqa-lider-general` + Atlassian MCP + Tablero `KAN` + Confluence Hub `6717610` | Backlog `KAN` trazado, metas SMART (`ICR >= 85%`, `DDA <= 15%`), fila 1 de gobernanza en `MONITOR_DINAMICO_TIEMPO_REAL` |
| **2. Ejecución** | Todos los líderes (foco en *Tester*: Andrés Cardozo) | `sqa-tester-dinamico` + `backend/TESTING.md` + `ci-sqa.yml` ejecutando `@Tag("unitaria")`, `@Tag("integracion")`, `@Tag("categoria")` y build Vue | Reportes Surefire separados en `target/sqa-reports/`, jobs en verde en GitHub Actions y suites listadas en el Monitor Web |
| **3. Dirección** | Gabriel López (*Líder General*) | Alertas inmediatas en **Discord** (`SQA CI/CD Bot` + `GitHub APP`), commits trazados `KAN-XX` y comentario automático en `KAN-69` | Canal de Discord con desglose completo por commit, autor y enlace directo al Monitor Web en vivo |
| **4. Monitoreo** | Gabriel López (*Líder General*, asistido por DevOp y Líder de Métricas) | `scripts/collect_ci_metrics.py` + `SqaRealtimeWebhook.gs` + publicación continua en `gh-pages` | Pestaña `Datos_CI_TiempoReal` + Dashboard `MONITOR_DINAMICO_TIEMPO_REAL` + Sitio `https://panzerog.github.io/Blog-Equipo-M6-PACS/` |
| **5. Control** | Gabriel López (*Líder General*, con soporte técnico DevOp) | Reglas de `quality_gate` (`VERDE`/`AMARILLO`/`ROJO`), aislamiento obligatorio de `backend/data/*.json` y retención de artefactos | Badge Semáforo en Sheets, Web y Discord; artefactos inmutables `sqa-backend-reports` y `sqa-final-metrics` |
| **6. Evaluación** | Rebeca López (*Escriba-Auditora*, junto a métricas de Nahomi Abella) | `sqa-escriba-auditor` + `sqa-metricas-monitor` + desglose ISO/IEC 25010 (`completitud`, `correccion`, `pertinencia`) + tabla de Validación Humana | Cobertura JaCoCo XML/HTML, historial evolutivo (`metrics-history.json`) y cálculo auditado de Tasa de Rechazo de IA |

---

## 7. Registro de Decisiones Arquitectónicas (ADRs)

- **ADR-01 — Aislamiento estricto de persistencia JSON en pruebas (`@ActiveProfiles("test")` + `@TempDir`):** Como *The Blog* persiste entidades en `backend/data/*.json`, cualquier prueba sin redirección corrompería los datos base de producción. Se impuso `application-test.properties` hacia `./target/test-data/*.json` y se blindó en `AGENTS.md` y `TESTING.md`.
- **ADR-02 — Agente Java estático `byte-buddy-agent` en `backend/pom.xml`:** Mockito 5.17 intentó auto-adjuntarse dinámicamente sobre Windows y bloqueó Maven Surefire (`ACCESS_DENIED`). Se fijó `-javaagent` estático en `maven-surefire-plugin` junto con `useModulePath=false` y `@{argLine}` para compatibilidad con JaCoCo tanto local como en Linux CI.
- **ADR-03 — Limpieza de `target/jacoco.exec` antes de la suite completa:** Previene acumulación anómala de contadores entre corridas parciales por `@Tag`, garantizando cobertura limpia y determinista (`38.14%` líneas en `10a9335`).
- **ADR-04 — Integración Google Sheets no destructiva + curl sin `-X POST`:** Se aislaron los datos CI en `Datos_CI_TiempoReal` y `MONITOR_DINAMICO_TIEMPO_REAL` para no interferir con `Datos_Jira_Raw`, `Datos_Checklists_Estaticas` ni `DASHBOARD_METRICAS_PACS`. En el workflow se utiliza `curl -fsSL` sin `-X POST` para seguir correctamente la redirección HTTP 302 de Google Apps Script tras `doPost(e)`.
- **ADR-05 — Prevención de bucles CI y runners Node 24:** Se configuró `branches-ignore: [ gh-pages ]` para evitar disparos recursivos al actualizar el dashboard estático y se migraron todas las acciones (`checkout@v5`, `setup-java@v5`, `setup-node@v5`, `upload-artifact@v6`, `download-artifact@v8`) logrando **0 advertencias de ejecución**.
