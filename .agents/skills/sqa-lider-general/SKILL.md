---
name: sqa-lider-general
description: >-
  Use this skill when the user (Líder General) asks for executive SQA status,
  project planning, direction, real-time monitoring, risk control, SMART goal
  tracking, or cross-role coordination across Jira KAN, CI/CD, and Confluence.
---

# SQA Líder General — Planificación, Dirección, Monitoreo y Control

Skill operativo para **Gabriel López (Líder General)**. Centraliza la visión gerencial del PACS sobre los procesos exigidos para la gestión del SQA (**Planificación, Ejecución, Dirección, Monitoreo, Control y Evaluación**).

## Pasos Obligatorios

1. **Auditar el tablero completo en Jira (`KAN`) vía MCP (`atlassian`):**
   - Consultar `searchJiraIssuesUsingJql` en `sqa-team-m6.atlassian.net` (`project = KAN ORDER BY updated DESC`) paginando hasta obtener todos los ítems activos.
   - Clasificar por estado (`Por hacer`, `En curso`, `Finalizado`), prioridad y responsable/rol:
     - Líder General (`rol:lider-general`)
     - Analista de Pruebas y Tester (`rol:lider-funcional`)
     - Líder Tecnológico / DevOp (`rol:lider-tecnologico`)
     - Líder de Métricas (`rol:lider-metricas`)
     - Escriba y Auditor (`rol:escriba`)

2. **Verificar estado técnico del CI y la documentación:**
   - Revisar métricas recientes de `backend/target/sqa-ci-metrics.json` (si existen en local) o consultar las páginas clave de Confluence (`04. Informe de Revisiones`, `05. Ecosistema Tecnológico, Métricas y Gobernanza`, `07. Instrumento de inspección Formal`, `08. Walkthrough`).
   - Identificar cuellos de botella (por ejemplo, defectos críticos `KAN-60` a `KAN-64` aún sin resolver o pruebas dinámicas pendientes por módulo).

3. **Evaluar los 6 Procesos de Gestión SQA y Objetivos SMART:**
   Emitir un Tablero Ejecutivo cubriendo:
   - **Planificación:** tareas definidas, fechas límite hacia la entrega (**14 de diciembre de 2026**) y cobertura de backlog en Jira.
   - **Ejecución:** porcentaje de avance real por rol y suite de pruebas ejecutada.
   - **Dirección:** asignaciones claras, dependencias cruzadas (p. ej. permisos Atlassian/GitHub) y decisiones requeridas.
   - **Monitoreo:** estado en tiempo real de Jira, Discord, CI y Dashboard de métricas.
   - **Control:** desviaciones frente a umbrales del PACS (`PCR >= 80%`, `ICR >= 85%`, `DDA <= 15%`) y acciones correctivas.
   - **Evaluación:** verificación junto al Escriba-Auditor de evidencias trazables y cumplimiento de objetivos SMART.

4. **Proponer Acciones Concretas en Jira:**
   Listar los ajustes de prioridad, reasignaciones o nuevas tareas de cierre recomendadas, solicitando confirmación explícita del Líder General antes de ejecutar mutaciones (`createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`) en Jira.
