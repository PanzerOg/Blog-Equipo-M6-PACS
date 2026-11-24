# Autoevaluación Crítica del Ecosistema Tecnológico y Agéntico (ISO/IEC 25010 e ISO/IEC 25059)

| Metadato | Detalle |
| :--- | :--- |
| **Proyecto** | Aseguramiento de la Calidad del Software (UCAB 2026-2) — Equipo M6 |
| **Objeto de Evaluación** | Ecosistema Tecnológico, CI/CD, Agentes y Monitor SQA para *The Blog* |
| **Responsable de Autoevaluación** | José Alejandro Montes de Oca Tineo — Líder Tecnológico / DevOp |
| **Marcos de Referencia** | ISO/IEC 25010 (Calidad de Producto Software) · ISO/IEC 25059 (Calidad de Sistemas con IA) · PACS Equipo M6 |
| **Línea Base Verificada** | Commits `6a73263` (CI), `a1fd8ff` (Agentes), `10a9335` (Monitor en Tiempo Real) · Jira `KAN-69` |

---

## 1. Línea Base Cuantitativa Observada en Producción

Antes de emitir los juicios de calidad, esta autoevaluación parte exclusivamente de los resultados reales ejecutados y verificados en el repositorio `PanzerOg/Blog-Equipo-M6-PACS`:

- **Pipeline CI/CD (`ci-sqa.yml`):** Ejecuciones en verde en `main` y `gh-pages`, con **0 advertencias de ejecución** tras migrar las acciones a Node 24 (`actions/checkout@v5`, `setup-java@v5`, `setup-node@v5`, `upload-artifact@v6`, `download-artifact@v8`).
- **Ejecución Semilla de Pruebas Dinámicas (`10a9335`):** **9/9 aprobadas (`Pass Rate = 100.0%`)**, clasificadas en `@Tag("unitaria")` (`3/3`), `@Tag("integracion")` (`3/3`) y `@Tag("categoria")` (`3/3`, con `1/1` en *Completitud*, *Corrección* y *Pertinencia Funcional*).
- **Cobertura JaCoCo Limpia (`10a9335`):** `38.14%` en líneas, `16.67%` en ramas, `32.09%` en instrucciones y `80.77%` en clases *(nota técnica: en la corrida #1 `6a73263` se observó `39.71%` líneas antes de introducir la limpieza explícita de `target/jacoco.exec` previa a la suite completa; a partir de `10a9335` la cifra es estrictamente determinista)*.
- **Monitores en Tiempo Real Activos:** Pestañas `Datos_CI_TiempoReal` y `MONITOR_DINAMICO_TIEMPO_REAL` operando en Google Sheets (`PACS-SQA-Dashboard-Metricas-KAN`), Dashboard Web vivo en `https://panzerog.github.io/Blog-Equipo-M6-PACS/` con 2 corridas históricas registradas y notificaciones enriquecidas del bot `SQA CI/CD Bot` en Discord.
- **Integración Atlassian:** Servidor MCP oficial (`atlassian`, `26 tools enabled`) con permisos `read-write` en Jira `KAN` y Confluence `6717610`, más `twg` CLI v1.4.6 validado.

---

## 2. Evaluación bajo ISO/IEC 25010 (Calidad del Ecosistema Tecnológico)

Escala de valoración interna del DevOp: **1** Deficiente · **2** Básico · **3** Funcional · **4** Sólido · **5** Sobresaliente (justificado con evidencia y brechas reales).

| Característica ISO/IEC 25010 | Puntaje | Evidencia y Fortalezas Verificadas | Brechas y Oportunidades de Mejora Identificadas |
| :--- | :---: | :--- | :--- |
| **1. Adecuación Funcional** | **4.5 / 5** | El ecosistema cubre planificación/gestión (Jira MCP), pruebas por categoría (`@Tag`), medición (JaCoCo + `collect_ci_metrics.py`), reporte en vivo (Sheets + `gh-pages`) y alertas (Discord), asistiendo los 6 procesos SQA de la Sección 13. | Falta automatizar la ejecución E2E sobre el frontend Vue en CI (actualmente se valida con `npm run build` y `npm run lint` diagnóstico). |
| **2. Eficiencia de Desempeño** | **4.5 / 5** | El pipeline completa compilación, 3 corridas segmentadas + suite JaCoCo, build frontend, webhook Sheets, despliegue `gh-pages` y notificación Discord en ~1 minuto gracias al caché Maven/npm en GitHub Actions; `SqaRealtimeWebhook.gs` usa `LockService` (20 s) y el dashboard refresca cada 60 s sin recargar la página. | Ejecutar 4 veces Maven en backend (`unitaria`, `integracion`, `categoria`, `suite completa`) es aceptable con 9 pruebas, pero conviene vigilar el tiempo total si la suite crece por encima de varios cientos de casos. |
| **3. Compatibilidad (Interoperabilidad y Coexistencia)** | **4.5 / 5** | Interoperabilidad verificada entre GitHub Actions, Python, Google Apps Script (`curl -fsSL` manejando redirección HTTP 302), Discord Webhook, GitHub Pages y Atlassian MCP/TWG. Coexistencia limpia en Google Sheets preservando `Datos_Jira_Raw`, `Datos_Checklists_Estaticas` y `DASHBOARD_METRICAS_PACS`. | La integración nativa *GitHub for Atlassian* en el panel Desarrollo de Jira permanece pendiente de aprobación del Site Admin (`Gabriel López`), aunque está mitigada operativamente por Smart Commits (`KAN-XX`) y Atlassian MCP. |
| **4. Usabilidad** | **4.0 / 5** | Cada líder dispone de un skill propio en `.agents/skills/`, guías paso a paso en `docs/`, semáforo visual único (`VERDE`/`AMARILLO`/`ROJO`) y un tablero web oscuro con acceso en un clic a Jira, Confluence, Sheets y Actions. | Los líderes deben editar manualmente `%USERPROFILE%\.gemini\config\mcp_config.json` en su máquina local la primera vez para conectar Atlassian MCP. |
| **5. Fiabilidad (Madurez, Tolerancia a Fallos y Recuperabilidad)** | **4.5 / 5** | `application-test.properties` y `@TempDir` aíslan completamente `backend/data/*.json`. `ci-sqa.yml` usa `set +e` para capturar reportes XML aun cuando una prueba falla, tolera ausencia de artefactos generando métricas mínimas y deduplica corridas por `run_id`/`commit_sha` tanto en `metrics-history.json` como en Google Sheets. | No existe reintento automático con backoff en la llamada `curl` al webhook de Apps Script ante un fallo transitorio de red de Google; además, `index.html` depende de CDN externo para Chart.js (degrada graciosamente ocultando gráficos si no hay conexión). |
| **6. Seguridad** | **4.0 / 5** | Los endpoints privados (`DISCORD_WEBHOOK_URL`, `GSHEETS_WEBHOOK_URL`) se almacenan cifrados en GitHub Secrets y nunca aparecen en el repositorio ni en expresiones `if:` de Actions. `SqaRealtimeWebhook.gs` soporta validación opcional por token compartido (`SQA_MONITOR_TOKEN` / `GSHEETS_WEBHOOK_TOKEN`) y `index.html` escapa cadenas HTML (`escapeHtml`) contra XSS. | Para publicar GitHub Pages en plan gratuito el repositorio debió configurarse como público (`Now open sourced!`). Aunque no hay secretos en el repo, se recomienda activar `GSHEETS_WEBHOOK_TOKEN` para evitar envíos externos no autorizados al `/exec` si alguien conociera su URL. |
| **7. Mantenibilidad (Modularidad, Analizabilidad, Modificabilidad)** | **4.5 / 5** | Lógica desacoplada en módulos claros: `scripts/collect_ci_metrics.py` (Python tipado sin dependencias externas), `SqaRealtimeWebhook.gs`, `monitor/dashboard/index.html`, `backend/TESTING.md` y 4 skills independientes. | `SqaRealtimeWebhook.gs` reside en el repo pero su copia activa en Apps Script debe pegarse manualmente cuando se actualiza el código del script. |
| **8. Portabilidad** | **4.5 / 5** | Las pruebas corren de forma equivalente en Windows 11 local (`mvnw.cmd`, JDK 22 compilando `release 17`, agente `byte-buddy-agent` estático) y en Linux `ubuntu-latest` CI (JDK 17 Temurin), respaldadas por artefactos reproducibles y Dockerfiles en `backend/` y `frontend/`. | Los scripts de la guía usan comandos PowerShell pensados para Windows; en macOS/Linux los líderes deben sustituir `.\mvnw.cmd` por `./mvnw`. |

**Promedio global del ecosistema bajo ISO/IEC 25010:** **4.38 / 5.00** *(Ecosistema integrado, automatizado, trazable y verificable)*.

---

## 3. Evaluación bajo ISO/IEC 25059 (Calidad de Sistemas con IA — Gobernanza Agéntica)

El proyecto incorpora agentes de IA (`Antigravity` + `AGENTS.md` + `.agents/skills/`). Evaluar esta capa bajo los principios de calidad para sistemas basados en IA (**ISO/IEC 25059**) permite evitar riesgos típicos como alucinaciones normativas, pérdida de trazabilidad o automatización destructiva:

| Dimensión ISO/IEC 25059 Aplicada | Valoración | Controles Implementados en el Ecosistema | Evidencia / Mecanismo de Verificación |
| :--- | :---: | :--- | :--- |
| **Controlabilidad y Supervisión Humana (*Human-in-the-Loop*)** | **Alta** | Ningún agente aprueba, cierra o hace push autónomo sin validación humana. `AGENTS.md` declara explícitamente toda salida de IA como propuesta sujeta a arbitraje humano del líder del rol correspondiente. | Protocolo obligatorio en `sqa-tester-dinamico` (*Tabla de Validación de Pertinencia Humana*) y ejecución explícita de `git commit`/`push` por el operador. |
| **Transparencia y Trazabilidad Agéntica** | **Alta** | El comportamiento agéntico no reside en prompts efímeros: está versionado en Git dentro de `AGENTS.md` y `.agents/skills/*/SKILL.md`, vinculando cada acción a un ticket `KAN-XX` y a Confluence `6717610`. | Comentarios reales en `KAN-69` generados vía MCP `atlassian` y mapa explícito de 4 roles en el repositorio. |
| **Robustez frente a Alucinaciones y Verificabilidad** | **Alta** | Regla de *Cero Invención* en `AGENTS.md`: prohíbe inventar endpoints, porcentajes o cláusulas normativas; exige citar archivos inspeccionados, salidas reales de comandos o consultas en vivo vía MCP. | Auditoría cruzada por **Rebeca López (`sqa-escriba-auditor`)**, quien calcula la **Tasa de Rechazo de IA** sobre propuestas de casos y reportes antes de la entrega final. |
| **Seguridad e Integridad de Datos en Operación Agéntica** | **Alta** | Aislamiento duro contra manipulación accidental de persistencia productiva (`backend/data/*.json`) mediante `AGENTS.md`, `TESTING.md` y `@ActiveProfiles("test")`. | Verificaciones locales y en CI mantienen `git diff --stat -- backend/data` limpio (`0` cambios). |
| **Adecuación Funcional de los Agentes por Rol** | **Media-Alta** | Segregación en 4 skills especializados (`tester-dinamico`, `escriba-auditor`, `metricas-monitor`, `lider-general`) alineados a responsabilidades reales del PACS y rúbrica. | Reducción de ambigüedad de contexto al operar sobre tareas acotadas; aún dependiente de que cada líder conecte su sesión MCP personal. |

---

## 4. Análisis Crítico Honesto: Limitaciones Actuales y Hoja de Ruta

Para sostener una defensa técnica rigurosa ante evaluación, se transparentan las **5 limitaciones actuales** del ecosistema y su plan de cierre antes del **14 de diciembre de 2026**:

1. **Cobertura actual de código Backend (`38.14%` líneas, `16.67%` ramas) inferior a la meta objetivo (`60%`):**
   - *Causa real:* El DevOp implementó las 3 suites semilla (9 pruebas) para validar la infraestructura CI/CD, `@Tag` y JaCoCo sin invadir el alcance funcional del Tester.
   - *Plan de cierre:* **Andrés Cardozo** (*Tester*) utilizará `sqa-tester-dinamico` y la infraestructura ya montada para añadir baterías unitarias, de integración y de categoría trazadas a `KAN-60`..`KAN-67` y elevar progresivamente el indicador visible en el Monitor Web.
2. **Validación Frontend acotada a compilación y lint (`npm run build`, `npm run lint` con `continue-on-error`):**
   - *Plan de cierre:* Evaluar con el Tester e incorporar pruebas E2E/componentes clave si se prioriza cobertura de interfaz sobre vistas de *The Blog* (*Adecuación Funcional — Pertinencia*).
3. **Aplicación *GitHub for Atlassian* pendiente en Jira (`Pendiente de configuración`):**
   - *Causa real:* Requiere aprobación del Site Admin de Jira (**Gabriel López**).
   - *Mitigación activa:* No bloquea la trazabilidad porque `KAN-69` ya documenta commits/avances vía MCP `atlassian` y cada commit porta el prefijo `KAN-XX`. Gabriel puede aprobarla en 2 minutos siguiendo el *Manual Maestro*.
4. **Endurecimiento del Webhook Google Apps Script (`SQA_MONITOR_TOKEN`):**
   - *Riesgo:* Sin token configurado, cualquier petición POST válida al URL `/exec` podría insertar filas en `Datos_CI_TiempoReal`.
   - *Plan de cierre:* Activar la propiedad `SQA_MONITOR_TOKEN` en Apps Script y el secret `GSHEETS_WEBHOOK_TOKEN` en GitHub.
5. **Dependencia de CDN en Chart.js y actualización manual de Apps Script:**
   - *Mitigación:* El dashboard web muestra igual todos los KPIs, tablas e indicadores ISO aunque Chart.js no cargue, y `SqaRealtimeWebhook.gs` permanece versionado en Git ante cualquier ajuste futuro.
