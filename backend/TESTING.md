# Pruebas unitarias del backend

## Preparacion

El backend ya incluye JUnit 5, Mockito y las utilidades de pruebas de Spring mediante
`spring-boot-starter-test`. Los tests nuevos van en `src/test/java`, respetando los
paquetes de `src/main/java`.

No se debe usar `backend/data` desde una prueba: contiene los datos de desarrollo.
Las pruebas que levanten Spring deben activar el perfil `test` con `@ActiveProfiles("test")`.
Ese perfil redirige los siete repositorios JSON a `target/test-data`, que Maven limpia
con `mvnw.cmd clean`.

## Aislamiento por tipo de prueba

- **Servicio:** crear la instancia del servicio e inyectar mocks de sus repositorios (y
  servicios colaboradores). Preparar el estado de cada caso con `when(...)` y verificar
  las llamadas con `verify(...)`. No iniciar Spring ni leer/escribir archivos.
- **Repositorio JSON:** usar `@TempDir` de JUnit 5 y construir el repositorio con una
  ruta dentro del directorio temporal del caso. Así cada caso obtiene archivos nuevos
  y no comparte estado con otros tests ni con `backend/data`.
- **Integracion con Spring:** activar el perfil `test`. Si el caso necesita verificar
  persistencia o crear datos, limpiar/restablecer su estado en `@BeforeEach` o asignar
  rutas temporales propias mediante propiedades de prueba. No depender del orden de
  ejecución ni de datos dejados por otro caso.

Para cubrir un módulo asociado a varias historias de usuario, organizar los tests por
servicio o comportamiento del módulo y convertir cada escenario de aceptación de las
historias en casos independientes: flujo exitoso, validaciones, límites y errores,
permisos y efectos sobre otros componentes cuando correspondan. Cada caso debe preparar
sus propios datos, ejecutar una acción y comprobar tanto el resultado como las
interacciones relevantes. Los colaboradores externos al comportamiento bajo prueba se
simulan; las pruebas de repositorio verifican por separado la serialización y
persistencia.

## Ejecucion

Desde `backend` en Windows:

```powershell
.\mvnw.cmd test
.\mvnw.cmd -Dtest=NombreDeLaClaseTest test
.\mvnw.cmd clean test
```

La primera orden ejecuta la suite completa, la segunda permite trabajar sobre una clase
o módulo, y la tercera vuelve a compilar desde cero antes de ejecutar. Una prueba no
debe requerir que se ejecute otra antes.

## Categorias JUnit 5 (`@Tag`) e Integracion Continua (CI)

El pipeline de GitHub Actions (`.github/workflows/ci-sqa.yml`) se dispara en cada `push` y
`pull_request` y ejecuta las pruebas separadas por etiquetas `@Tag` de JUnit 5:

| Bloque en CI | Etiqueta obligatoria | Subetiquetas recomendadas (ISO/IEC 25010) | Alcance |
| :--- | :--- | :--- | :--- |
| **Pruebas Unitarias** | `@Tag("unitaria")` | — | Servicios/modelos aislados con Mockito, sin Spring ni archivos. |
| **Pruebas de Integracion** | `@Tag("integracion")` | — | Contexto Spring con `@ActiveProfiles("test")`, `MockMvc` y JSON en `target/test-data` o `@TempDir`. |
| **Pruebas por Categorias** | `@Tag("categoria")` | `@Tag("completitud")`, `@Tag("correccion")`, `@Tag("pertinencia")` | Casos orientados a subcaracteristicas de Adecuacion Funcional y hallazgos (`KAN-60` a `KAN-67`). |

### Ejecucion por categoria en Windows

```powershell
.\mvnw.cmd test -Dgroups=unitaria -DfailIfNoTests=true
.\mvnw.cmd test -Dgroups=integracion -DfailIfNoTests=true
.\mvnw.cmd test -Dgroups=categoria -DfailIfNoTests=true
.\mvnw.cmd test -Dgroups=completitud
.\mvnw.cmd clean test jacoco:report
```

El reporte HTML y XML de cobertura JaCoCo queda en `backend/target/site/jacoco/` y los
reportes Surefire en `backend/target/surefire-reports/`.
