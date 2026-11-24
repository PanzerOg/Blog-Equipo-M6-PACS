/**
 * SQA Equipo M6 - Webhook de Telemetria CI/CD hacia Google Sheets
 * Repositorio: PanzerOg/Blog-Equipo-M6-PACS
 * Hoja destino: https://docs.google.com/spreadsheets/d/1J43xxO0YiiuszPSXeSoiPlpE4fHGS6JPRqDo9Q19mVU/edit
 *
 * IMPORTANTE: Este script NO modifica ni elimina la pestaña existente "Datos_Jira_Raw"
 * ni otras pestañas de Fase 1. Solo crea/actualiza "Datos_CI_TiempoReal" y
 * "MONITOR_DINAMICO_TIEMPO_REAL".
 */

var SPREADSHEET_ID = "1J43xxO0YiiuszPSXeSoiPlpE4fHGS6JPRqDo9Q19mVU";
var SHEET_RAW_CI = "Datos_CI_TiempoReal";
var SHEET_DASHBOARD = "MONITOR_DINAMICO_TIEMPO_REAL";

var CI_HEADERS = [
  "Timestamp_UTC",
  "Run_ID",
  "Commit",
  "Rama",
  "Autor",
  "Mensaje_Commit",
  "Semaforo_SQA",
  "Backend_Status",
  "Frontend_Status",
  "Pruebas_Totales",
  "Pruebas_Aprobadas",
  "Pruebas_Fallidas",
  "Pass_Rate_Pct",
  "Unitarias_Aprobadas",
  "Unitarias_Total",
  "Integracion_Aprobadas",
  "Integracion_Total",
  "Categoria_Aprobadas",
  "Categoria_Total",
  "Completitud_Pct",
  "Correccion_Pct",
  "Pertinencia_Pct",
  "JaCoCo_Lineas_Pct",
  "JaCoCo_Ramas_Pct",
  "Run_URL"
];

/**
 * Responde a peticiones GET de verificacion de estado del webhook.
 */
function doGet(e) {
  var ss = getTargetSpreadsheet_();
  var sheets = ss.getSheets().map(function (s) { return s.getName(); });
  return jsonResponse_({
    ok: true,
    service: "SQA M6 Monitor Webhook",
    spreadsheetId: ss.getId(),
    sheets: sheets,
    targetSheets: [SHEET_RAW_CI, SHEET_DASHBOARD]
  });
}

/**
 * Recibe metricas JSON desde GitHub Actions y actualiza Google Sheets en tiempo real.
 */
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var rawBody = (e && e.postData && e.postData.contents) ? e.postData.contents : "{}";
    var payload = JSON.parse(rawBody);

    var expectedToken = PropertiesService.getScriptProperties().getProperty("SQA_MONITOR_TOKEN");
    if (expectedToken && expectedToken.trim() !== "") {
      var providedToken = payload.token || (e && e.parameter ? e.parameter.token : "");
      if (providedToken !== expectedToken.trim()) {
        return jsonResponse_({ ok: false, error: "Token de autorizacion invalido" });
      }
    }

    var ss = getTargetSpreadsheet_();
    var sheets = ensureSheets_(ss);
    var rawSheet = sheets.rawSheet;

    var rowValues = buildCiRow_(payload);
    var runId = String(payload.run_id || "");
    var existingRow = findRowByRunId_(rawSheet, runId);

    if (existingRow > 1) {
      rawSheet.getRange(existingRow, 1, 1, CI_HEADERS.length).setValues([rowValues]);
    } else {
      rawSheet.appendRow(rowValues);
    }

    return jsonResponse_({
      ok: true,
      action: existingRow > 1 ? "updated" : "appended",
      run_id: runId,
      commit: rowValues[2],
      quality_gate: rowValues[6],
      sheet: SHEET_RAW_CI
    });
  } catch (err) {
    return jsonResponse_({
      ok: false,
      error: String(err && err.message ? err.message : err)
    });
  } finally {
    lock.releaseLock();
  }
}

/**
 * Permite inicializar o reparar manualmente las pestañas del monitor desde el editor de Apps Script.
 */
function setupSqaRealtimeSheets() {
  var ss = getTargetSpreadsheet_();
  ensureSheets_(ss);
  return "Pestañas verificadas: " + SHEET_RAW_CI + " y " + SHEET_DASHBOARD;
}

function getTargetSpreadsheet_() {
  try {
    var active = SpreadsheetApp.getActiveSpreadsheet();
    if (active && active.getId() === SPREADSHEET_ID) {
      return active;
    }
  } catch (ignore) {}
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function ensureSheets_(ss) {
  var rawSheet = ss.getSheetByName(SHEET_RAW_CI);
  if (!rawSheet) {
    rawSheet = ss.insertSheet(SHEET_RAW_CI);
  }
  configureRawSheet_(rawSheet);

  var dashSheet = ss.getSheetByName(SHEET_DASHBOARD);
  if (!dashSheet) {
    dashSheet = ss.insertSheet(SHEET_DASHBOARD);
    configureDashboardSheet_(dashSheet);
  }

  return { rawSheet: rawSheet, dashSheet: dashSheet };
}

function configureRawSheet_(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, CI_HEADERS.length).setValues([CI_HEADERS]);
    sheet.getRange(1, 1, 1, CI_HEADERS.length)
      .setBackground("#0F172A")
      .setFontColor("#F8FAFC")
      .setFontWeight("bold");
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, CI_HEADERS.length);
  }
}

function configureDashboardSheet_(sheet) {
  sheet.clear();
  sheet.getRange("A1:F1").merge()
    .setValue("MONITOR DINAMICO SQA EN TIEMPO REAL — THE BLOG (EQUIPO M6 | ISO/IEC 25010)")
    .setBackground("#0F172A")
    .setFontColor("#F8FAFC")
    .setFontSize(13)
    .setFontWeight("bold")
    .setHorizontalAlignment("center");

  var latestFormula = function (colLetter) {
    return '=IF(COUNTA(' + SHEET_RAW_CI + '!A:A)<=1,"EN ESPERA",IFERROR(INDEX(' + SHEET_RAW_CI + '!' + colLetter + ':' + colLetter + ',COUNTA(' + SHEET_RAW_CI + '!A:A)),"EN ESPERA"))';
  };
  var latestNumFormula = function (colLetter) {
    return '=IF(COUNTA(' + SHEET_RAW_CI + '!A:A)<=1,0,IFERROR(INDEX(' + SHEET_RAW_CI + '!' + colLetter + ':' + colLetter + ',COUNTA(' + SHEET_RAW_CI + '!A:A)),0))';
  };

  var kpiRows = [
    ["Indicador Clave CI/CD", "Valor Actual", "Meta PACS / ISO 25010", "Ultima Corrida", "Estado / Detalle", "Fuente"],
    ["Semaforo Global SQA", latestFormula("G"), "VERDE", "Commit", latestFormula("C"), "GitHub Actions"],
    ["Tasa de Aprobacion (Pass Rate %)", latestNumFormula("M"), ">= 85% (ICR)", "Rama", latestFormula("D"), "JUnit 5 Surefire"],
    ["Pruebas Aprobadas", latestNumFormula("K"), "100% sin fallos", "Total Pruebas", latestNumFormula("J"), "Unit + Int + Cat"],
    ["Pruebas Fallidas + Errores", latestNumFormula("L"), "0 fallos (DDA <= 15%)", "Timestamp UTC", latestFormula("A"), "Surefire XML"],
    ["Cobertura Lineas JaCoCo (%)", latestNumFormula("W"), ">= 60% objetivo (>= 30% piso)", "Backend CI", latestFormula("H"), "JaCoCo XML"],
    ["Cobertura Ramas JaCoCo (%)", latestNumFormula("X"), "Crecimiento continuo", "Frontend CI", latestFormula("I"), "Vue Build CI"]
  ];
  sheet.getRange(3, 1, kpiRows.length, 6).setValues(kpiRows);
  sheet.getRange(3, 1, 1, 6).setBackground("#1E293B").setFontColor("#E2E8F0").setFontWeight("bold");

  var catRows = [
    ["Desglose por Tipo y Subcaracteristica ISO/IEC 25010", "Aprobadas", "Totales", "Cumplimiento (%)", "Relacion con el Sistema", "Tag JUnit"],
    ["Pruebas Unitarias", latestNumFormula("N"), latestNumFormula("O"), '=IFERROR(ROUND((B12/C12)*100,2),0)', "Logica de servicios aislada", "@Tag('unitaria')"],
    ["Pruebas de Integracion", latestNumFormula("P"), latestNumFormula("Q"), '=IFERROR(ROUND((B13/C13)*100,2),0)', "Flujos MockMvc + contexto Test", "@Tag('integracion')"],
    ["Pruebas por Categorias ISO 25010", latestNumFormula("R"), latestNumFormula("S"), '=IFERROR(ROUND((B14/C14)*100,2),0)', "Adecuacion Funcional global", "@Tag('categoria')"],
    ["Subcaracteristica: Completitud Funcional", "-", "-", latestNumFormula("T"), "Cobertura de tareas y endpoints", "@Tag('completitud')"],
    ["Subcaracteristica: Correccion Funcional", "-", "-", latestNumFormula("U"), "Precision de datos y reglas", "@Tag('correccion')"],
    ["Subcaracteristica: Pertinencia Funcional", "-", "-", latestNumFormula("V"), "Idoneidad para roles reales", "@Tag('pertinencia')"]
  ];
  sheet.getRange(11, 1, catRows.length, 6).setValues(catRows);
  sheet.getRange(11, 1, 1, 6).setBackground("#1E293B").setFontColor("#E2E8F0").setFontWeight("bold");

  var processRows = [
    ["Proceso de Gestion SQA (Seccion 13)", "Responsable", "Mecanismo Automatizado", "Evidencia / Enlace", "Ultima Validacion", "Estado Operativo"],
    ["1. Planificacion", "Gabriel Lopez (Lider General)", "PACS + Backlog KAN en Jira", "Atlassian MCP / Confluence", latestFormula("A"), '=IF(COUNTA(' + SHEET_RAW_CI + '!A:A)>1,"ACTIVO","PENDIENTE")'],
    ["2. Ejecucion", "Andres Cardozo (Lider Funcional)", "Suites JUnit 5 (@Tag unitaria/integracion/categoria)", "ci-sqa.yml (Ubuntu JDK 17)", latestFormula("C"), latestFormula("H")],
    ["3. Direccion", "Gabriel Lopez & Jose Montes de Oca", "Alertas automaticas en Discord + Kanban Jira", "Discord Webhook + KAN-69", latestFormula("E"), latestFormula("G")],
    ["4. Monitoreo", "Jose Montes de Oca (Lider DevOp)", "Colector Python + Sheets Webhook + Dashboard Web", "Datos_CI_TiempoReal", latestFormula("A"), '=IF(COUNTA(' + SHEET_RAW_CI + '!A:A)>1,"EN LINEA","EN ESPERA")'],
    ["5. Control", "Rebeca Lopez (Escriba-Auditora)", "Semaforo SQA + Artefactos inmutables Surefire/JaCoCo", latestFormula("Y"), latestFormula("G"), latestFormula("G")],
    ["6. Evaluacion", "Nahomi Abella (Lider de Metricas)", "Analisis ISO/IEC 25010 (Completitud/Correccion/Pertinencia) + JaCoCo", "MONITOR_DINAMICO_TIEMPO_REAL", latestNumFormula("W"), '=IF(B8>=30,"CONFORME","BAJO UMBRAL")']
  ];
  sheet.getRange(19, 1, processRows.length, 6).setValues(processRows);
  sheet.getRange(19, 1, 1, 6).setBackground("#1E293B").setFontColor("#E2E8F0").setFontWeight("bold");

  applyConditionalRules_(sheet);
  sheet.autoResizeColumns(1, 6);
}

function applyConditionalRules_(sheet) {
  var gateRange = sheet.getRange("B4");
  var covRange = sheet.getRange("B8:B9");
  var rules = [];

  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo("VERDE")
      .setBackground("#DCFCE7")
      .setFontColor("#166534")
      .setBold(true)
      .setRanges([gateRange])
      .build()
  );
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo("AMARILLO")
      .setBackground("#FEF9C3")
      .setFontColor("#854D0E")
      .setBold(true)
      .setRanges([gateRange])
      .build()
  );
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo("ROJO")
      .setBackground("#FEE2E2")
      .setFontColor("#991B1B")
      .setBold(true)
      .setRanges([gateRange])
      .build()
  );
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenNumberGreaterThanOrEqualTo(60)
      .setBackground("#DCFCE7")
      .setFontColor("#166534")
      .setRanges([covRange])
      .build()
  );
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenNumberBetween(30, 59.99)
      .setBackground("#FEF9C3")
      .setFontColor("#854D0E")
      .setRanges([covRange])
      .build()
  );
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenNumberLessThan(30)
      .setBackground("#FEE2E2")
      .setFontColor("#991B1B")
      .setRanges([covRange])
      .build()
  );
  sheet.setConditionalFormatRules(rules);
}

function subPct_(isoObj, key) {
  if (!isoObj || !isoObj[key] || !isoObj[key].total) {
    return 0;
  }
  return Math.round((Number(isoObj[key].passed || 0) / Number(isoObj[key].total)) * 10000) / 100;
}

function buildCiRow_(payload) {
  var byCat = payload.by_category || {};
  var uni = byCat.unitaria || {};
  var integ = byCat.integracion || {};
  var cat = byCat.categoria || {};
  var iso = payload.iso_25010_adecuacion_funcional || {};

  var failures = Number(payload.tests_failures || 0) + Number(payload.tests_errors || 0);
  return [
    payload.timestamp_utc || new Date().toISOString(),
    String(payload.run_id || ""),
    String(payload.commit_short || payload.commit_sha || ""),
    String(payload.branch || "main"),
    String(payload.actor || ""),
    String(payload.commit_message || ""),
    String(payload.quality_gate || "AMARILLO"),
    String(payload.backend_status || "unknown"),
    String(payload.frontend_status || "unknown"),
    Number(payload.tests_total || 0),
    Number(payload.tests_passed || 0),
    failures,
    Number(payload.pass_rate_pct || 0),
    Number(uni.passed || 0),
    Number(uni.total || 0),
    Number(integ.passed || 0),
    Number(integ.total || 0),
    Number(cat.passed || 0),
    Number(cat.total || 0),
    subPct_(iso, "completitud"),
    subPct_(iso, "correccion"),
    subPct_(iso, "pertinencia"),
    Number(payload.line_coverage_pct || 0),
    Number(payload.branch_coverage_pct || 0),
    String(payload.run_url || "")
  ];
}

function findRowByRunId_(sheet, runId) {
  if (!runId) {
    return -1;
  }
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    return -1;
  }
  var runIds = sheet.getRange(2, 2, lastRow - 1, 1).getValues();
  for (var i = 0; i < runIds.length; i++) {
    if (String(runIds[i][0]) === runId) {
      return i + 2;
    }
  }
  return -1;
}

function jsonResponse_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
