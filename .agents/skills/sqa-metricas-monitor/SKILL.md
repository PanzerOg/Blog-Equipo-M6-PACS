---
name: sqa-metricas-monitor
description: >-
  Use this skill when the user (Líder de Métricas) asks to collect, compute, or
  interpret project, process, and product quality metrics from Jira KAN,
  Surefire test reports, JaCoCo coverage, or sqa-ci-metrics.json for live
  dashboards and the PACS report.
---

# SQA Líder de Métricas — Consolidación Estadística y Monitor en Tiempo Real

Skill operativo para **Nahomi Abella (Líder de Métricas)**. Extrae evidencia verificable de **Jira (`KAN`)**, **Surefire** y **JaCoCo** para calcular los indicadores de **Proyecto**, **Proceso** y **Producto** con sus umbrales de control.

## Pasos Obligatorios

1. **Consultar datos reales en Jira vía MCP (`atlassian`):**
   - Ejecutar `searchJiraIssuesUsingJql` en `sqa-team-m6.atlassian.net` para:
     - Todas las tareas e incidencias del proyecto: `project = KAN ORDER BY created DESC` (paginar hasta `isLast: true`).
     - Defectos de código estático: `project = KAN AND issuetype = Error AND labels = "fase:codigo"`.
     - Defectos de pruebas dinámicas: `project = KAN AND issuetype = Error AND labels = "fase:dinamica"`.
   - Agrupar conteos reales por estado (`Por hacer`, `En curso`, `Finalizado`), prioridad (`High`, `Medium`, `Low`) y etiqueta de rol (`rol:*`).

2. **Leer métricas reales de ejecución dinámica en el repositorio:**
   - Si existe, leer `backend/target/sqa-ci-metrics.json`.
   - Si no existe o se requiere cálculo local actualizado, inspeccionar `backend/target/surefire-reports/TEST-*.xml` y `backend/target/site/jacoco/jacoco.xml` (o correr `.\mvnw.cmd clean test jacoco:report` desde `backend/`).
   - No inventar cifras: si un archivo de reporte no está generado aún, indicarlo explícitamente.

3. **Calcular el Cuadro Consolidado en los 3 Niveles (con Umbrales):**
   - **Métricas de Proyecto:**
     - `% Cumplimiento Cronograma SQA (PCR) = (Tareas Finalizadas / Total Tareas Planificadas) * 100` (Meta: `>= 80%`).
     - Distribución de carga y avance por rol (`rol:*`).
   - **Métricas de Proceso:**
     - Cobertura de ejecución por bloque CI (`unitaria`, `integracion`, `categoria`).
     - `Tasa de Detección Temprana (TDT)` vs. fuga de defectos a fase dinámica (`Defectos Estáticos / Total Defectos`).
     - `Tasa de Rechazo de IA (%)` (coordinada con `sqa-escriba-auditor`).
   - **Métricas de Producto (Adecuación Funcional — ISO/IEC 25010):**
     - `Tasa de Aprobación de Pruebas Dinámicas (Pass Rate %) = (Pruebas Aprobadas / Total Ejecutadas) * 100`.
     - `Cobertura de Líneas y Ramas JaCoCo (%)` extraída de `jacoco.xml`.
     - `Densidad de Defectos Dinámicos` por módulo/subcaracterística (`Completitud`, `Corrección`, `Pertinencia`).
     - Comparativa evolutiva frente a la línea base estática (`IAFP` del Instrumento de Inspección Formal).

4. **Formatear Salida Lista para Dashboard (Google Sheets + Confluence):**
   - Entregar una tabla limpia con: `Categoría | Métrica | Fórmula | Valor Medido | Umbral Objetivo | Estado (Verde/Amarillo/Rojo) | Fuente Verificable`.
   - Incluir un bloque resumen listo para actualizar la página `05. Ecosistema Tecnológico, Métricas y Gobernanza` (`6717610`) de Confluence o la hoja `PACS-SQA-Dashboard-Metricas-KAN`.
