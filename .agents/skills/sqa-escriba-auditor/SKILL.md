---
name: sqa-escriba-auditor
description: >-
  Use this skill when the user (Escriba y Auditora) asks to audit AI-generated
  outputs, calculate AI rejection rates, verify anti-hallucination compliance,
  review Confluence or PACS metadata under ISO/IEC/IEEE 15289 and IEEE 730, or
  prepare an audit report.
---

# SQA Escriba y Auditor — Conformidad Documental y Calidad de Uso de IA

Skill operativo para **Rebeca López (Escriba y Auditora)**. Asegura la conformidad documental bajo **IEEE Std 730** e **ISO/IEC/IEEE 15289**, ejecuta la verificación cruzada anti-alucinación y calcula las métricas de auditoría y **tasa de rechazo de salidas de IA** requeridas en el proyecto final.

## Pasos Obligatorios

1. **Recopilar los artefactos a auditar:**
   - Leer las páginas relevantes de Confluence vía MCP `atlassian` (`searchConfluence`, `getConfluenceContent`), por ejemplo:
     - `04. Informe de Revisiones` (`6914049`)
     - `05. Ecosistema Tecnológico, Métricas y Gobernanza` (`6717610`)
     - `07. Instrumento de inspección Formal` (`16941062`)
     - `07.1 Inspección de Código asistida por Agente IA (KAN-58)` (`16416769`)
     - `08. Walkthrough` (`18448385`)
   - Consultar los tickets relacionados en Jira (`searchJiraIssuesUsingJql` en `project = KAN`) y los archivos del repositorio (`backend/TESTING.md`, `backend/src/test/java/`, `backend/target/sqa-ci-metrics.json`).

2. **Ejecutar Verificación Cruzada Anti-Alucinación (4 Controles):**
   Para cada afirmación o propuesta generada por IA en documentos o pruebas:
   - **Control de código:** ¿El archivo, clase, método o endpoint citado existe literalmente en el repositorio?
   - **Control de Jira/Confluence:** ¿La clave `KAN-XX` y su estado/prioridad coinciden con lo consultado en vivo vía MCP?
   - **Control de métricas:** ¿Los conteos de pruebas y cobertura coinciden con `backend/target/surefire-reports/` y `backend/target/site/jacoco/jacoco.xml`?
   - **Control normativo:** ¿Las referencias a estándares (ISO/IEC 25010, ISO/IEC/IEEE 29119, 29148, 42010, 15289, 12207, IEEE 730, ISO/IEC 25059) corresponden a normas reales del curso sin inventar numerales?

3. **Verificar Metadatos de Control Documental (ISO/IEC/IEEE 15289):**
   Comprobar que todo entregable formal incluya: identificador único, versión, fecha de emisión, autor(es) por rol, revisor, aprobador, estado e historial de cambios.

4. **Calcular la Matriz de Auditoría de IA y Tasa de Rechazo:**
   Consolidar los registros de arbitraje humano (propuestas de pruebas del Tester, textos asistidos, análisis de métricas) y calcular explícitamente:
   - `Total de Propuestas Evaluadas (N)`
   - `Aceptadas sin cambios (A)` | `Aceptadas con ajustes (AJ)` | `Rechazadas (R)`
   - `Tasa de Rechazo IA (%) = (R / N) * 100`
   - `Tasa de Ajuste IA (%) = (AJ / N) * 100`
   - Clasificar cada rechazo por causa raíz: `Alucinación técnica`, `Referencia normativa inválida`, `Fuera de dominio/ERS`, `Redundancia`, `Fallo de aislamiento de datos`.

5. **Emitir Informe de Hallazgos de Auditoría:**
   Presentar un dictamen estructurado (`Conforme`, `Conforme con Observaciones` o `No Conforme`), lista de hallazgos trazables listos para registrar en Jira/Confluence y acciones correctivas con responsable.
