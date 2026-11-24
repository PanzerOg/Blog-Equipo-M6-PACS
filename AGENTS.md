# Gobernanza Agéntica — Proyecto SQA *The Blog* (Equipo M6, UCAB 2026-2)

Este archivo define las reglas obligatorias para cualquier agente o asistente de IA que trabaje dentro de este repositorio (`PanzerOg/Blog-Equipo-M6-PACS`).

## 1. Sistema Bajo Evaluación y Foco de Calidad
- **Sistema:** *The Blog* — Backend en **Java 17 / Spring Boot 3.5.6** con persistencia en archivos JSON (`backend/src/main/java/com/software/spring/`) y Frontend en **Vue 3 / Vue Router** (`frontend/src/`).
- **Característica de calidad principal:** **Adecuación Funcional** (ISO/IEC 25010), operacionalizada en sus tres subcaracterísticas:
  1. **Completitud Funcional** (`@Tag("completitud")`)
  2. **Corrección Funcional** (`@Tag("correccion")`)
  3. **Pertinencia Funcional** (`@Tag("pertinencia")`)
- **Estándares de referencia del proyecto (no citar cláusulas sin verificarlas en el texto oficial):**
  - ISO/IEC 25010 (modelo de calidad de producto) e ISO/IEC 25059 (calidad de sistemas con IA)
  - ISO/IEC/IEEE 29119 (Partes 1–4: conceptos, procesos, documentación y técnicas de prueba)
  - ISO/IEC/IEEE 29148 (requisitos), ISO/IEC/IEEE 42010 (arquitectura), ISO/IEC/IEEE 15289 (documentación), ISO/IEC/IEEE 12207 (ciclo de vida) e IEEE Std 730 (PACS)

## 2. Reglas Inviolables de Pruebas y Aislamiento de Datos
1. **Prohibido leer, escribir o alterar `backend/data/*.json`** desde cualquier prueba automatizada.
2. Toda prueba de integración que levante el contexto de Spring debe usar `@ActiveProfiles("test")` (que redirige la persistencia a `backend/target/test-data/`) o `@TempDir` de JUnit 5 al instanciar repositorios JSON.
3. Toda prueba nueva en `backend/src/test/java/` debe cumplir `backend/TESTING.md` y llevar obligatoriamente al menos una etiqueta JUnit 5 principal de CI:
   - `@Tag("unitaria")` — Servicios o modelos aislados con Mockito, sin Spring ni I/O en disco.
   - `@Tag("integracion")` — Contexto Spring con `@ActiveProfiles("test")`, `MockMvc` o repositorios en `@TempDir`.
   - `@Tag("categoria")` — Acompañada de `@Tag("completitud")`, `@Tag("correccion")` o `@Tag("pertinencia")`.
4. Antes de proponer un commit, validar localmente desde `backend/`:
   - `.\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true`
   - `.\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true`
   - `.\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true`
   - `.\mvnw.cmd clean test jacoco:report`

## 3. Gobernanza MCP y Trazabilidad Estática ↔ Dinámica
- **Atlassian MCP (`atlassian`):** Sitio oficial `https://sqa-team-m6.atlassian.net`, proyecto Jira **`KAN`**.
- Antes de diseñar casos de prueba, reportar métricas o auditar entregables, consultar en vivo Jira/Confluence vía MCP (`atlassian`) para mantener trazabilidad con los **8 defectos de inspección estática de código (`KAN-60` a `KAN-67`)** y los artefactos de Fase 1 (`KAN-24` a `KAN-53`).
- Incluir la clave del ticket (`KAN-XX`) al inicio de cada mensaje de commit.

## 4. Protocolo Anti-Alucinación y Supervisión Humana
1. Toda salida generada por IA (casos de prueba, tablas de especificaciones, hallazgos o redacción de informes) es una **propuesta sujeta a arbitraje humano** por el líder responsable.
2. **Cero invención:** nunca fabricar endpoints, nombres de clases/métodos, porcentajes de cobertura, resultados de pruebas ni cláusulas normativas. Citar únicamente archivos inspeccionados, salidas reales de comandos o respuestas reales del MCP `atlassian`.
3. Toda propuesta de casos generada para el Tester debe incluir la tabla de **Validación de Pertinencia Humana** para que el Escriba-Auditor pueda calcular la tasa de rechazo de IA.

## 5. Mapa de Skills Especializados por Rol (`.agents/skills/`)
- **Analista de Pruebas y Tester (Andrés Cardozo):** `.agents/skills/sqa-tester-dinamico/SKILL.md`
- **Escriba y Auditora (Rebeca López):** `.agents/skills/sqa-escriba-auditor/SKILL.md`
- **Líder de Métricas (Nahomi Abella):** `.agents/skills/sqa-metricas-monitor/SKILL.md`
- **Líder General (Gabriel López):** `.agents/skills/sqa-lider-general/SKILL.md`
