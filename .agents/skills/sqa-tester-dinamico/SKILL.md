---
name: sqa-tester-dinamico
description: >-
  Use this skill when the user (Analista de Pruebas y Tester) asks to design,
  trace, generate, or execute JUnit 5 dynamic tests (unit, integration, or
  functional suitability category tests) for The Blog linked to Jira KAN-60..KAN-67
  and ISO/IEC/IEEE 29119-4 techniques.
---

# SQA Tester Dinámico — Diseño y Automatización de Pruebas (*The Blog*)

Skill operativo para **Andrés Cardozo (Analista de Pruebas y Tester)**. Articula la trazabilidad estática↔dinámica mediante el servidor MCP `atlassian`, la norma **ISO/IEC/IEEE 29119-4**, las subcaracterísticas de **Adecuación Funcional (ISO/IEC 25010)** y el pipeline CI en Maven/JUnit 5.

## Pasos Obligatorios

1. **Consultar trazabilidad estática en Jira vía MCP (`atlassian`):**
   - Ejecutar `searchJiraIssuesUsingJql` sobre `cloudId: "sqa-team-m6.atlassian.net"` con `jql: "project = KAN AND labels = \"fase:codigo\" ORDER BY key ASC"` (o revisar `KAN-60` a `KAN-67`).
   - Identificar las reglas de negocio afectadas, criterios de aceptación, endpoints y severidad de cada hallazgo.

2. **Inspeccionar el código real antes de diseñar pruebas:**
   - Leer las clases reales involucradas en `backend/src/main/java/com/software/spring/` (`controller`, `service`, `repository`, `model`) y las vistas en `frontend/src/views/` si aplica.
   - Nunca asumir firmas, DTOs ni códigos HTTP sin leer el archivo fuente.

3. **Construir la Tabla de Especificaciones y Casuística (ISO/IEC/IEEE 29119-4):**
   Antes de escribir código de prueba, presentar una tabla con estas columnas exactas:
   - `ID Caso`
   - `HU / Ticket Jira (KAN-XX)`
   - `Subcaracterística ISO 25010` (`Completitud` | `Corrección` | `Pertinencia`)
   - `Nivel` (`Unitaria` | `Integración` | `Sistema`)
   - `Enfoque` (`Caja Blanca` | `Caja Negra` | `Caja Gris`)
   - `Técnica ISO 29119-4` (Partición de equivalencia, Valores límite, Tabla de decisión, Transición de estados, Cobertura de sentencias/ramas)
   - `Resultado Esperado vs. Comportamiento Actual`

4. **Implementar los tests JUnit 5 cumpliendo `backend/TESTING.md`:**
   - Respetar paquetes bajo `backend/src/test/java/com/software/spring/`.
   - **Aislamiento estricto:** nunca acceder a `backend/data/*.json`.
     - Unitarias (`@Tag("unitaria")`): usar `@ExtendWith(MockitoExtension.class)` y mocks; sin levantar Spring ni tocar disco.
     - Integración (`@Tag("integracion")`): usar `@SpringBootTest`, `@AutoConfigureMockMvc`, `@ActiveProfiles("test")` o `@TempDir`, limpiando el archivo JSON de prueba en `@BeforeEach`.
     - Categorías (`@Tag("categoria")`): añadir además `@Tag("completitud")`, `@Tag("correccion")` o `@Tag("pertinencia")`.
   - En pruebas orientadas a capturar defectos abiertos (p. ej. `KAN-60` a `KAN-67`), documentar explícitamente en comentarios Javadoc si el caso valida el comportamiento esperado según ERS (y falla mientras el defecto siga abierto) o si verifica la regresión una vez corregido.

5. **Emitir el Bloque de Validación de Pertinencia Humana (Obligatorio):**
   Al final de cada propuesta generada con IA, incluir la siguiente tabla para revisión de Andrés y auditoría de Rebeca:

   | ID Caso | Propuesto por IA | Pertinente (Sí/No) | Decisión (Aceptado / Ajustado / Rechazado) | Motivo del Arbitraje |
   | :--- | :---: | :---: | :---: | :--- |
   | `TC-...` | Sí | `[Pendiente]` | `[Pendiente]` | — |

6. **Ejecutar verificación real en Maven y reportar hallazgos dinámicos:**
   - Correr desde `backend/`:
     ```powershell
     .\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true
     .\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true
     .\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true
     .\mvnw.cmd clean test jacoco:report
     ```
   - Si una prueba revela una falla nueva no registrada en Jira, proponer el borrador del ticket tipo `Error` en `KAN` con etiqueta `fase:dinamica` y severidad/prioridad según ISO/IEC/IEEE 29119-3 antes de crearlo con `createJiraIssue`.
