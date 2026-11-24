# Guía de Uso del Ecosistema Agéntico y MCP — Equipo SQA M6 (*The Blog*)

Esta guía permite a todos los líderes del equipo (**Gabriel López**, **Andrés Cardozo**, **Nahomi Abella** y **Rebeca López**) trabajar sobre el repositorio `PanzerOg/Blog-Equipo-M6-PACS` con **Antigravity / Antigravity IDE**, **Atlassian MCP** y el **CI de GitHub Actions**.

---

## 1. Qué ya viene configurado dentro del repositorio

Al clonar o actualizar (`git pull origin main`) este repositorio, **Antigravity** descubre automáticamente:

- **`AGENTS.md`:** Reglas obligatorias del proyecto (aislamiento de `backend/data/`, etiquetas `@Tag` de JUnit 5, trazabilidad a `KAN-XX` y protocolo anti-alucinación).
- **`.agents/skills/`:** Cuatro skills especializados por rol:
  - `sqa-tester-dinamico` → **Andrés Cardozo (Analista de Pruebas y Tester)**
  - `sqa-escriba-auditor` → **Rebeca López (Escriba y Auditora)**
  - `sqa-metricas-monitor` → **Nahomi Abella (Líder de Métricas)**
  - `sqa-lider-general` → **Gabriel López (Líder General)**
- **`backend/TESTING.md` y `.github/workflows/ci-sqa.yml`:** Pipeline CI automático que en cada `git push` ejecuta por separado pruebas `unitaria`, `integracion`, `categoria` (ISO 25010), cobertura JaCoCo, build del frontend Vue y notificación a Discord.

---

## 2. Configuración inicial en tu máquina (una sola vez, 3 minutos)

### Paso A: Clonar / actualizar el repositorio y abrirlo en Antigravity
```powershell
git clone https://github.com/PanzerOg/Blog-Equipo-M6-PACS.git
cd Blog-Equipo-M6-PACS
```
*(Si ya lo tienes clonado, ejecuta `git pull origin main`).* Luego abre esa carpeta en **Antigravity** o **Antigravity IDE**.

### Paso B: Configurar tu correo Git para trazabilidad
Usa el mismo correo UCAB con el que accedes a Jira (`sqa-team-m6.atlassian.net`):
```powershell
git config user.email "tu.correo@est.ucab.edu.ve"
```

### Paso C: Conectar el MCP oficial de Atlassian (Jira + Confluence)
1. Abre tu archivo global de configuración MCP:
   - Windows: `%USERPROFILE%\.gemini\config\mcp_config.json`
   - macOS/Linux: `~/.gemini/config/mcp_config.json`
2. Agrega la entrada `"atlassian"` dentro de `"mcpServers"` (conservando cualquier otro servidor que ya tengas):
   ```json
   {
     "mcpServers": {
       "atlassian": {
         "url": "https://mcp.atlassian.com/v2/mcp"
       }
     }
   }
   ```
3. Guarda el archivo.
4. En Antigravity abre **Additional Options (`...`) → MCP Servers → Manage MCP Servers** (o **Skills & Customizations → MCP Servers**), haz clic en **Refresh** y luego en **Authenticate** junto a `atlassian` para iniciar sesión con tu cuenta de `sqa-team-m6.atlassian.net`.
5. Verifica que aparezca en verde (`26 tools enabled`).

---

## 3. Cómo usar el Agente de tu Rol (Prompts recomendados)

### Para Andrés Cardozo — Analista de Pruebas y Tester (`sqa-tester-dinamico`)
> *"Usa el skill `sqa-tester-dinamico`. Consulta en Jira vía MCP los hallazgos KAN-60 al KAN-67, lee los controladores y servicios afectados en `backend/`, construye la tabla de especificaciones (Adecuación Funcional × técnicas ISO 29119-4) para la HU de Comentarios y genera las pruebas JUnit 5 etiquetadas con `@Tag` junto con la tabla de validación de pertinencia humana."*

### Para Rebeca López — Escriba y Auditora (`sqa-escriba-auditor`)
> *"Usa el skill `sqa-escriba-auditor`. Revisa los resultados de las pruebas propuestas y las páginas de Confluence del proyecto; verifica que no haya alucinaciones ni referencias inválidas a estándares, valida los metadatos ISO 15289 y calcula la matriz de Tasa de Rechazo de IA."*

### Para Nahomi Abella — Líder de Métricas (`sqa-metricas-monitor`)
> *"Usa el skill `sqa-metricas-monitor`. Consulta en Jira vía MCP las incidencias del proyecto KAN y lee los reportes locales de Surefire y JaCoCo para calcular las métricas de proyecto, proceso y producto con sus semáforos de umbral listos para Google Sheets y Confluence."*

### Para Gabriel López — Líder General (`sqa-lider-general`)
> *"Usa el skill `sqa-lider-general`. Consulta todo el tablero KAN en Jira vía MCP agrupado por rol y genera el reporte ejecutivo de planificación, ejecución, dirección, monitoreo, control y evaluación frente a los objetivos SMART del PACS."*

---

## 4. Flujo de Trabajo para Subir Pruebas y Disponer del CI

1. Al crear pruebas en `backend/src/test/java/`, nunca leas ni modifiques `backend/data/*.json`.
2. Valida localmente desde `backend/`:
   ```powershell
   .\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true
   .\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true
   .\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true
   ```
3. Haz commit incluyendo la clave de Jira (`KAN-XX`) y sube tu rama o `main`:
   ```powershell
   git add .
   git commit -m "KAN-XX Agregar pruebas dinamicas de ..."
   git push
   ```
4. Revisa la ejecución automática en **GitHub → Actions → SQA CI - Pruebas Dinamicas y Calidad** y la alerta en **Discord**.
