# Manual Maestro de Operación del Ecosistema SQA — Equipo M6 (*The Blog*)

| Metadato ISO/IEC/IEEE 15289 | Valor |
| :--- | :--- |
| **Propósito** | Guía operativa unificada para que los 4 líderes del equipo utilicen el ecosistema CI/CD, Atlassian MCP, Monitor en Tiempo Real y Agentes |
| **Destinatarios** | Gabriel López (*Líder General*), Andrés Cardozo (*Tester*), Nahomi Abella (*Métricas*), Rebeca López (*Escriba-Auditora*) |
| **Elaborado por** | José Alejandro Montes de Oca Tineo — Líder Tecnológico / DevOp (`KAN-69`) |
| **Complementa a** | [GUIA_ECOSISTEMA_AGENTICO.md](GUIA_ECOSISTEMA_AGENTICO.md) · [AGENTS.md](../AGENTS.md) · [backend/TESTING.md](../backend/TESTING.md) |
| **Fecha límite de entrega final** | Lunes 14 de diciembre de 2026 — 23:55 (Módulo 7) |

---

## 1. Panel Central de Accesos del Ecosistema

Guarda estos enlaces en favoritos; todos están interconectados en vivo tras cada `git push` en `main`:

| Componente | Enlace Oficial | Uso Principal |
| :--- | :--- | :--- |
| **Monitor Web en Tiempo Real** | https://panzerog.github.io/Blog-Equipo-M6-PACS/ | Semáforo SQA, KPIs, desglose ISO 25010, gráficos JaCoCo, 6 procesos SQA e historial de corridas |
| **Google Sheets Dinámico** | https://docs.google.com/spreadsheets/d/1J43xxO0YiiuszPSXeSoiPlpE4fHGS6JPRqDo9Q19mVU/edit | Pestañas `Datos_CI_TiempoReal` y `MONITOR_DINAMICO_TIEMPO_REAL` (además de `Datos_Jira_Raw`, `Datos_Checklists_Estaticas` y `DASHBOARD_METRICAS_PACS`) |
| **Dashboard Sheets Fase 1** | https://noashigod.github.io/Dashboard_SQA_M6_sheet/ | Referencia de métricas de Jira de la Fase 1 |
| **Repositorio GitHub** | https://github.com/PanzerOg/Blog-Equipo-M6-PACS | Código fuente de *The Blog*, pruebas JUnit 5, skills agénticos y documentación |
| **Pipeline GitHub Actions** | https://github.com/PanzerOg/Blog-Equipo-M6-PACS/actions | Ejecución de pruebas `@Tag`, build Vue, descarga de reportes Surefire/JaCoCo |
| **Tablero Jira (`KAN`)** | https://sqa-team-m6.atlassian.net/jira/software/projects/KAN/boards | Backlog, hallazgos estáticos (`KAN-60`..`KAN-67`), tareas DevOp (`KAN-69`) y hallazgos dinámicos |
| **Confluence Hub** | https://sqa-team-m6.atlassian.net/wiki/spaces/SQA/pages/6717610 | Página `05. Ecosistema Tecnológico, Métricas y Gobernanza` y actas de revisión |
| **Canal Discord del Equipo** | Canal con webhooks configurados (`GitHub APP` + `SQA CI/CD Bot`) | Alertas instantáneas por cada commit con Semáforo, conteo por `@Tag` y cobertura JaCoCo |

---

## 2. Configuración Inicial Común en tu Máquina (5 minutos, una sola vez)

1. **Clonar o actualizar el repositorio y abrirlo en Antigravity / Antigravity IDE:**
   ```powershell
   git clone https://github.com/PanzerOg/Blog-Equipo-M6-PACS.git
   cd Blog-Equipo-M6-PACS
   ```
   *(Si ya lo tenías clonado, ejecuta `git pull origin main`).* Abre esa carpeta raíz como workspace en Antigravity para que cargue automáticamente `AGENTS.md` y los 4 skills de `.agents/skills/`.

2. **Configurar tu correo UCAB en Git (trazabilidad de autoría):**
   ```powershell
   git config user.name "Tu Nombre"
   git config user.email "tu.correo@est.ucab.edu.ve"
   ```

3. **Conectar el servidor MCP oficial de Atlassian (`atlassian`) en Antigravity:**
   - Edita `%USERPROFILE%\.gemini\config\mcp_config.json` (Windows) o `~/.gemini/config/mcp_config.json` (macOS/Linux) y agrega dentro de `"mcpServers"`:
     ```json
     {
       "mcpServers": {
         "atlassian": {
           "url": "https://mcp.atlassian.com/v2/mcp"
         }
       }
     }
     ```
   - En Antigravity abre **MCP Servers → Manage MCP Servers → Refresh → Authenticate** junto a `atlassian`, inicia sesión con tu cuenta UCAB de `sqa-team-m6.atlassian.net` y confirma que aparezca en verde (`26 tools enabled`).

4. **(Opcional) Instalar Atlassian Teamwork Graph CLI (`twg`):**
   Útil si deseas consultar Jira desde PowerShell con `twg work query` o verificar salud con `twg doctor`. Para trabajo normal dentro de Antigravity IDE, el MCP `atlassian` del paso 3 ya cubre todo sin pasos adicionales.

---

## 3. Playbooks Operativos Paso a Paso por Rol

### 3.1 Para Andrés Cardozo — Líder Funcional / Analista de Pruebas y Tester
- **Tu skill asignado:** `sqa-tester-dinamico` ([SKILL.md](../.agents/skills/sqa-tester-dinamico/SKILL.md))
- **Reglas técnicas obligatorias ([TESTING.md](../backend/TESTING.md) y [AGENTS.md](../AGENTS.md)):**
  - **NUNCA** leas ni modifiques `backend/data/*.json` desde ninguna prueba.
  - Pruebas unitarias (`@Tag("unitaria")`): usa `@ExtendWith(MockitoExtension.class)` y mocks; sin levantar Spring ni disco.
  - Pruebas de integración (`@Tag("integracion")`): usa `@SpringBootTest`, `@AutoConfigureMockMvc`, `@ActiveProfiles("test")` *(redirige JSON a `backend/target/test-data/`)* o `@TempDir`.
  - Pruebas de categoría ISO/IEC 25010 (`@Tag("categoria")`): acompaña **siempre** cada método o clase con `@Tag("completitud")`, `@Tag("correccion")` o `@Tag("pertinencia")` y nombra los métodos incluyendo la subcaracterística (`completitud_...`, `correccion_...`, `pertinencia_...`) para que el colector automático `collect_ci_metrics.py` las contabilice exactamente en el dashboard y en Sheets.
- **Tu flujo de trabajo con el agente:**
  1. Invoca en Antigravity:
     > *"Usa el skill `sqa-tester-dinamico`. Consulta vía MCP los tickets `KAN-60` al `KAN-67`, lee las clases reales en `backend/src/main/java/com/software/spring/` y construye la tabla de especificaciones (ISO 25010 × técnicas ISO/IEC/IEEE 29119-4) para el módulo X junto con el bloque de Validación de Pertinencia Humana."*
  2. **Arbitraje humano obligatorio:** Revisa los casos propuestos, marca cada uno como `Aceptado`, `Ajustado` o `Rechazado` en la tabla de pertinencia y guarda esa evidencia para que Rebeca calcule la *Tasa de Rechazo de IA*.
  3. **Validación local antes del push (desde `backend/`):**
     ```powershell
     .\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true
     .\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true
     .\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true
     .\mvnw.cmd clean test jacoco:report
     ```
     *(En macOS/Linux sustituye `.\mvnw.cmd` por `./mvnw`).*
  4. Verifica `git diff --stat -- backend/data` (debe salir vacío) y sube con la clave del ticket:
     ```powershell
     git add backend/src/test/
     git commit -m "KAN-XX Agregar pruebas unitarias, integracion y categoria para ..."
     git push origin main
     ```
  5. Si una prueba detecta un defecto nuevo del sistema, pide al agente redactar el ticket tipo `Error` en `KAN` (etiqueta `fase:dinamica`) y apruébalo antes de crearlo por MCP.

---

### 3.2 Para Rebeca López — Escriba y Auditora
- **Tu skill asignado:** `sqa-escriba-auditor` ([SKILL.md](../.agents/skills/sqa-escriba-auditor/SKILL.md))
- **Qué controlas en el ecosistema:**
  1. **Auditoría anti-alucinación sobre artefactos con IA:** Verificas código real citado, existencia de tickets `KAN-XX` en vivo vía MCP, cifras reales contra Surefire/JaCoCo y uso correcto de estándares (**ISO/IEC 25010, ISO/IEC 25059, ISO/IEC/IEEE 29119, 29148, 42010, 15289, 12207, IEEE 730**) sin cláusulas inventadas.
  2. **Cálculo oficial de Tasa de Rechazo de IA:** Recoges las tablas de *Validación de Pertinencia Humana* completadas por Andrés y aplicas con el agente:
     - `Tasa de Rechazo IA (%) = (R / N) * 100`
     - `Tasa de Ajuste IA (%) = (AJ / N) * 100`
     clasificando causas (`Alucinación técnica`, `Referencia normativa inválida`, `Fuera de dominio/ERS`, `Redundancia`, `Fallo de aislamiento de datos`).
  3. **Verificación de metadatos ISO/IEC/IEEE 15289 y descarga de artefactos inmutables:**
     - Entra en **GitHub Actions → última corrida en verde → Artifacts**: descarga **`sqa-backend-reports`** (contiene `surefire-reports/`, `sqa-reports/`, reporte navegable HTML `site/jacoco/index.html` y `sqa-ci-metrics.json`) y **`sqa-final-metrics`** (`final-sqa-metrics.json`) para respaldar cada auditoría y el informe final.
  4. **Prompt recomendado:**
     > *"Usa el skill `sqa-escriba-auditor`. Audita el entregable/propuesta X verificando las páginas de Confluence (`6717610`, `6914049`, `16941062`, `18448385`), los tickets `KAN` y los reportes reales del repositorio; valida metadatos ISO 15289 y calcula la matriz de Tasa de Rechazo de IA."*

---

### 3.3 Para Nahomi Abella — Líder de Métricas
- **Tu skill asignado:** `sqa-metricas-monitor` ([SKILL.md](../.agents/skills/sqa-metricas-monitor/SKILL.md))
- **Qué tienes disponible automáticamente en tiempo real:**
  - **En Google Sheets (`PACS-SQA-Dashboard-Metricas-KAN`):**
    - Tus pestañas de Fase 1 (`Datos_Jira_Raw`, `Datos_Checklists_Estaticas`, `DASHBOARD_METRICAS_PACS`) permanecen intactas.
    - La pestaña **`Datos_CI_TiempoReal`** recibe automáticamente una fila nueva (con 25 columnas) en cada corrida CI: `Timestamp_UTC`, `Run_ID`, `Commit`, `Rama`, `Autor`, `Mensaje_Commit`, `Semaforo_SQA`, `Backend_Status`, `Frontend_Status`, `Pruebas_Totales`, `Pruebas_Aprobadas`, `Pruebas_Fallidas`, `Pass_Rate_Pct`, `Unitarias_*`, `Integracion_*`, `Categoria_*`, `Completitud_Pct`, `Correccion_Pct`, `Pertinencia_Pct`, `JaCoCo_Lineas_Pct`, `JaCoCo_Ramas_Pct` y `Run_URL`.
    - La pestaña **`MONITOR_DINAMICO_TIEMPO_REAL`** calcula automáticamente con fórmulas `INDEX`/`IFERROR` el semáforo global, cumplimiento por `@Tag` / subcaracterística ISO 25010 y cobertura JaCoCo con formato condicional. **Regla:** evita sobrescribir manualmente las columnas `A:Y` de `Datos_CI_TiempoReal`; si deseas gráficos adicionales, referencia esas celdas desde `DASHBOARD_METRICAS_PACS` o una pestaña nueva de análisis.
  - **En el Monitor Web (`https://panzerog.github.io/Blog-Equipo-M6-PACS/`):**
    - Consulta la tendencia gráfica de `JaCoCo Lineas (%)`, `JaCoCo Ramas (%)`, `Pass Rate (%)` y apilado por categoría a lo largo de hasta las últimas 50 corridas (`data/metrics-history.json`).
- **Umbrales del Semáforo SQA implementados (`collect_ci_metrics.py`):**
  - **VERDE:** Todas las pruebas pasan (`0` fallos, `0` errores, `0` omitidas), `tests_total > 0`, cobertura de líneas JaCoCo `>= 30.0%` *(piso CI; meta del equipo `>= 60%`)*, y jobs Backend + Frontend en `success`.
  - **AMARILLO:** Pruebas aprobadas pero con casos omitidos (`skipped > 0`), cobertura de líneas `< 30.0%` o algún job en estado parcial/advertencia.
  - **ROJO:** `tests_total == 0`, al menos 1 fallo/error de prueba o fallo/cancelación de Backend o Frontend en CI.
- **Prompt recomendado:**
  > *"Usa el skill `sqa-metricas-monitor`. Consulta en Jira vía MCP todas las incidencias del proyecto `KAN`, revisa el último JSON de métricas CI y genera la tabla consolidada de Proyecto (PCR), Proceso (TDT y Tasa de Rechazo IA) y Producto (Pass Rate, JaCoCo, IAFP/Adecuación Funcional) lista para Confluence y Sheets."*

---

### 3.4 Para Gabriel López — Líder General
- **Tu skill asignado:** `sqa-lider-general` ([SKILL.md](../.agents/skills/sqa-lider-general/SKILL.md))
- **Monitoreo continuo de los 6 Procesos de Gestión SQA (Sección 13):**
  1. Abre https://panzerog.github.io/Blog-Equipo-M6-PACS/ o `MONITOR_DINAMICO_TIEMPO_REAL` en Google Sheets para revisar en tiempo real la tabla de **Planificación, Ejecución, Dirección, Monitoreo, Control y Evaluación**.
  2. Supervisa alertas en **Discord** tras cada push del equipo sin necesidad de entrar a Jenkins/Maven manualmente.
  3. Usa Antigravity con el prompt:
     > *"Usa el skill `sqa-lider-general`. Consulta todo el tablero `KAN` en Jira vía MCP agrupado por rol y estado, revisa la última línea base en Confluence y emite el reporte ejecutivo de cumplimiento frente a los objetivos SMART del PACS rumbo al 14 de diciembre."*

- **Acción rápida pendiente de Site Admin — Aprobar `GitHub for Atlassian` en Jira (2 minutos):**
  Durante Fase 2 quedó registrada en Jira la app `GitHub for Atlassian` como *"Pendiente de configuración"*. Para enlazar automáticamente las ramas, commits y PRs dentro de cada ticket `KAN-XX` en el panel derecho **Desarrollo**:
  1. Inicia sesión en Jira (`https://sqa-team-m6.atlassian.net`) con tu cuenta administradora (**Gabriel López**).
  2. Ve a **Configuración del sitio (engranaje superior derecho) → Aplicaciones → Administrar aplicaciones** (o entra directo desde **Desarrollo → Conexiones → GitHub for Atlassian → Configurar**).
  3. Autoriza la organización/repositorio **`PanzerOg/Blog-Equipo-M6-PACS`** cuando el conector OAuth de GitHub solicite acceso.
  4. Al completar ese enlace, las confirmaciones que comiencen con `KAN-60`, `KAN-69`, etc. aparecerán también en la tarjeta de Desarrollo de cada ticket de Jira.

---

## 4. Qué Hacer Si el Pipeline CI Sale en ROJO o AMARILLO

1. **Abre el enlace del embed en Discord** (*"Pipeline CI The Blog — ROJO"* te lleva directo a la corrida exacta en GitHub Actions).
2. Revisa cuál job falló:
   - Si falló **`Backend - Unitarias, Integracion, Categorias y JaCoCo`**: abre el step rojo (`1`, `2`, `3` o `4`) o revisa la tabla del **Job Summary** / artifact `sqa-backend-reports`. Corrige el código o la prueba localmente con `.\mvnw.cmd test` y vuelve a hacer push.
   - Si falló **`Frontend - Build Vue.js`**: entra en `frontend/` y corre `npm ci && npm run build` localmente para reproducir el error de sintaxis o dependencia.
   - Si falló **`Publicar Monitor en Tiempo Real (Sheets + Pages)`** en el paso de Google Sheets: verifica que el secret `GSHEETS_WEBHOOK_URL` siga apuntando a la implementación `/exec` vigente en Google Apps Script y que el permiso esté en *"Cualquier usuario"*.
3. Mientras tanto, ni `Datos_CI_TiempoReal` ni Discord dejan de reportar: el workflow usa `if: always()` para visibilizar inmediatamente cualquier caída (`ROJO`).

---

## 5. Preguntas Frecuentes (FAQ)

- **¿Por qué no debo tocar `backend/data/*.json`?**
  Porque es la base de datos JSON de la aplicación *The Blog*. Todas las pruebas automatizadas deben correr contra `@ActiveProfiles("test")` (`backend/target/test-data/`) o `@TempDir`.
- **¿Por qué si corro tests locales me funciona y en otros repositorios Mockito se queda colgado?**
  En `backend/pom.xml` el DevOp ya dejó configurado `byte-buddy-agent` como `-javaagent` estático y `useModulePath=false`, evitando el bloqueo de auto-adjuntado en Windows/JDK recientes. Si ejecutas pruebas desde IntelliJ/VS Code/Antigravity con Maven (`.\mvnw.cmd test`), funcionarán sin cuelgues.
- **¿Puedo cambiar un nombre de columna en `Datos_CI_TiempoReal`?**
  No directamente en la hoja, porque el orden posicional de las 25 columnas está acoplado a `CI_HEADERS` en [SqaRealtimeWebhook.gs](../monitor/google-apps-script/SqaRealtimeWebhook.gs) y a las fórmulas de `MONITOR_DINAMICO_TIEMPO_REAL`. Si necesitas nuevas columnas o métricas, pídelo al DevOp para actualizarlo de forma sincronizada.
- **¿Dónde reviso las reglas completas antes de generar pruebas con IA?**
  Lee [AGENTS.md](../AGENTS.md) y [backend/TESTING.md](../backend/TESTING.md).

---

## 6. Hoja de Referencia Rápida de Comandos (PowerShell)

```powershell
# 1. Actualizar repositorio antes de trabajar
git pull origin main

# 2. Validar pruebas backend por categoría (desde backend/)
Set-Location backend
.\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true
.\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true
.\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true
.\mvnw.cmd clean test jacoco:report
Set-Location ..

# 3. Verificar que NO se alteró backend/data/*.json
git diff --stat -- backend/data

# 4. Validar build del frontend Vue (desde frontend/)
Set-Location frontend
npm run build
Set-Location ..

# 5. Subir cambios con trazabilidad Jira (KAN-XX)
git status -s
git add .
git commit -m "KAN-XX Descripcion clara del cambio"
git push origin main
```
