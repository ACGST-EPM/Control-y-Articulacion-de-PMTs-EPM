# Plataforma de Control y Articulación de PMTs — Grupo EPM
## Documento maestro de traspaso
### Para continuar el desarrollo en un Proyecto de Claude y en Claude Code

> **Qué es esto:** el estado final y completo de todo lo construido, pensado para (1) cargarse como conocimiento en un **Proyecto de Claude** y (2) guiar el trabajo en **Claude Code**. Incluye objetivo, arquitectura, funcionalidades, especificaciones técnicas críticas, restricciones, limitaciones, pros y contras, mejoras posibles, el pendiente de **SEGURIDAD**, el historial de fases, la guía para continuar, y al final el **código definitivo** de cada archivo.

**Grupo EPM · Centro de Gestión Servicios Técnicos**
Repositorio publicado: `ACGST-EPM/Control-y-Articulacion-de-PMTs-EPM` (GitHub Pages)
Carpeta de trabajo local: `C:\Users\lmarinza\PLATAFORMA_PMTs`

---

## 0. Cómo usar este documento
- **Como conocimiento del Proyecto de Claude:** súbelo tal cual. Contiene el contexto y el código.
- **Con Claude Code:** el archivo corto `CLAUDE.md` (en la raíz del repositorio) es la memoria operativa; este documento es la referencia profunda a la que ese archivo remite.

---

## 1. Objetivo de la herramienta
Automatizar el control de los **Planes de Manejo de Tránsito (PMTs)**: capturar de forma estandarizada los datos de cada trazado de obra, **detectar conflictos** espaciales y temporales entre frentes de contratos distintos, y **visualizarlos** en un dashboard web con mapa, línea de tiempo, filtros e informe ejecutivo. El fin último es evitar que dos obras intervengan la misma zona al mismo tiempo sin coordinación.

---

## 2. Arquitectura y flujo de datos

```
[Contratista dibuja geometría en Google Earth]  →  KMZ con geometría
                         │
                         ▼
   Generador_KMZ.html (navegador)
   - Base maestra: contratos_db.json
   - Menús validados (sin texto libre)
   - Normaliza fechas / tipo_cierre
   - Exporta KMZ estandarizado
                         │  KMZ estandarizado
                         ▼
   C:\...\PLATAFORMA_PMTs\01_KMZ_Entrada
                         │
                         ▼
   proceso_pmt_qgis.py (Consola Python de QGIS)
   - Lee todos los .kmz de la carpeta
   - Detecta interferencias/cercanías (~120 m)
   - Genera capas del mapa + reporte
        │                         │
        │ reporte_dinamico.csv    │ capas → qgis2web
        ▼                         ▼
   repo\reporte_dinamico.csv   mapa web (qgis2web)
        │
        ▼
   Plataforma_PMTs.html (GitHub Pages)
   - Tabla + filtros cruzados + línea de tiempo
   - Informe PDF ejecutivo
   - Botón → abre Generador_KMZ.html
```

Publicación: todos los archivos web se suben con **GitHub Desktop** desde el clon local en `C:` (nunca editar por la web de GitHub en paralelo).

---

## 3. Inventario FINAL de archivos

| Archivo | Rol | Ubicación | Estado |
|---|---|---|---|
| `Generador_KMZ.html` | Captura estandarizada y generación de KMZ | raíz del repo | Definitivo |
| `Plataforma_PMTs.html` | Dashboard (antes `Plataforma.html`) | raíz del repo | Definitivo |
| `proceso_pmt_qgis.py` | Motor de análisis QGIS | `02_Proyecto_QGIS` (no se publica) | Definitivo |
| `contratos_db.json` | Base maestra de contratos | raíz del repo | Plantilla incluida |
| `reporte_dinamico.csv` | Salida del motor que alimenta el dashboard | raíz del repo | Se regenera al correr QGIS |
| `CLAUDE.md` | Memoria de proyecto para Claude Code | raíz del repo | Nuevo |
| `DOCUMENTACION_Plataforma_PMTs_EPM.md` | Este documento maestro | documental / raíz | Definitivo |
| `Optimizacion_Numeral4_Captura_KMZ.docx` | Análisis de 3 alternativas del numeral 4 | documental | Definitivo |

> **Cambio de nombre:** `Plataforma.html` pasó a llamarse **`Plataforma_PMTs.html`** para estandarizar frente a un desarrollo paralelo (otro tipo de permisos). No hubo referencias internas al nombre, así que el contenido quedó idéntico.

---

## 4. Funcionalidades por componente

### 4.1 `Generador_KMZ.html`
Reemplaza la escritura manual del campo *Descripción* del KMZ por menús validados.
- Base maestra editable (contrato → contratista, proyecto, municipios), con importar/exportar `contratos_db.json`.
- Geometría: **importar** KMZ/KML de Google Earth (preciso) o **dibujar** línea/punto en el mapa.
- Datos validados: contrato (auto-completa contratista/proyecto/municipios), tipo de cierre (lista cerrada), fechas con selector, dirección.
- **Municipios múltiples** por contrato (elige uno por trazado).
- **Duplicar para nueva vigencia** (clona geometría y datos, cambia solo fechas).
- **Validación** previa a exportar.
- **Clave de administrador** para editar la base maestra.
- Normaliza `24:00:00` → `00:00:00` del día siguiente, unifica mayúsculas de `tipo_cierre` y protege el separador `|`.
- Al guardar, reconoce una línea dibujada aunque no se haya cerrado con doble-clic.

### 4.2 `proceso_pmt_qgis.py`
Se pega y ejecuta en la Consola de Python de QGIS.
- Lee todos los `.kmz` de la carpeta de entrada.
- Detecta **interferencia real** (cruce espacial + solape temporal entre contratos distintos) y **cercanía** (cruce espacial sin solape temporal); ignora conflictos dentro del mismo contrato.
- Genera capas con propiedades temporales (línea de tiempo) y el reporte CSV.
- Los trazados `ingreso y salida` se dibujan como **punto azul circular** (`#0066CC`); si vienen como línea, usa su centroide.

### 4.3 `Plataforma_PMTs.html`
Dashboard que lee `reporte_dinamico.csv`.
- Filtros Select2 con **facetas cruzadas**: Contratista, Contrato, Frente, Interferencia/Estado y **Municipio**; al elegir uno, los demás se acotan.
- Rango de fechas, botón **Limpiar Filtros**.
- **Línea de tiempo / recorrido** temporal.
- **Informe PDF ejecutivo** (arma su propia tabla; no depende de la tabla visible).
- Exportación a Excel (incluye Municipio).
- Botón **🛠️ Generar KMZ** que abre el generador.

---

## 5. Especificaciones técnicas críticas
> Si se cambia una punta, hay que actualizar la otra. Esto es lo que mantiene compatibles al generador, el motor y el dashboard.

- **Formato de Descripción del KMZ:**
  `fecha_inicio: AAAA-MM-DD HH:MM:SS | fecha_fin: AAAA-MM-DD HH:MM:SS | tipo_cierre: <total|parcial|ingreso y salida> | direccion: <texto> | municipio: <texto> | contrato: <código> | contratista: <nombre> | proyecto: <nombre>`
  Separador ` | `. El orden es indiferente para el motor (lee por expresiones regulares). `municipio` solo si tiene valor.
- **Esquema `contratos_db.json`:** lista de objetos `{ "contrato", "contratista", "proyecto", "municipios": [ ... ] }`. El formato antiguo `{ "municipio": "X" }` se migra solo a `{ "municipios": ["X"] }`.
- **Lista cerrada `tipo_cierre`:** `total`, `parcial`, `ingreso y salida` (variable `TIPOS_CIERRE`; ya no se cachea en el navegador).
- **Clave del generador:** por defecto `EPM-PMT-2026`, guardada como huella SHA-256 en `CLAVE_HASH`. Es control de proceso, **no** seguridad real.
- **Columnas del CSV** (índices 0..10): `CATEGORIA, CONTRATO, CONTRATISTA, MUNICIPIO, FRENTE, DIRECCION, ESTADO_CIERRE, HORARIO, FECHA_INICIO, FECHA_FIN, DURACION_DIAS`.
- **Rutas del motor:** una sola línea `BASE = r"C:\Users\lmarinza\PLATAFORMA_PMTs"`; de ahí derivan `01_KMZ_Entrada` y la carpeta del repo (donde se guarda el CSV).
- **Capas QGIS (nombres exactos):** `🚀 GESTIÓN PMT MAESTRA`, `📍 INGRESO Y SALIDA`, `🔵 CERCANÍA (120m)`, `🟠 INTERFERENCIA REAL`, `📋 REPORTE DINÁMICO`.
- **Marca EPM:** verde `#009300`, lima `#b7c200`, naranja `#d56b00`.

---

## 6. Restricciones
- **Hosting estático:** GitHub Pages sirve archivos públicos; no ejecuta código de servidor ni protege datos. Cualquiera con la URL puede descargar el CSV. La "clave" del generador solo ordena el proceso, no protege información.
- **Entorno de un equipo:** el motor tiene la ruta fija a `C:\Users\lmarinza`; en otro PC hay que cambiar `BASE`.
- **Corrida manual:** el motor se ejecuta a mano en QGIS y el mapa se reexporta a mano con qgis2web.
- **Gobierno de datos corporativo:** al ser información de EPM, cualquier alojamiento en nubes de terceros o autenticación debe coordinarse con TI/Seguridad.

---

## 7. Limitaciones conocidas
**Generador:** clave client-side (no segura); la base se cachea por navegador (el archivo compartido es `contratos_db.json`, que hay que exportar y subir a mano); geometría dibujada a mano menos precisa que Google Earth; asume **un proyecto por contrato**; solo soporta punto y línea (no polígonos); al importar KML ignora estilos.
**Motor QGIS:** ruta fija a un equipo; ejecución manual; reexport qgis2web manual; buffer de ~120 m en grados (aproximación, no metros exactos); las filas de interferencia llevan municipio `"Varios"` (quedan fuera al filtrar por un municipio específico).
**Dashboard:** lee un CSV estático (datos solo cambian al re-correr QGIS y subir el CSV); el filtro Municipio depende de que el KMZ traiga municipio (los trazados viejos aparecen como `No definido`).

---

## 8. Pros y contras

| Aspecto | Pros | Contras |
|---|---|---|
| Hosting (GitHub Pages) | Gratis, simple, sin servidor, fácil de publicar | Público; no autentica ni protege datos |
| Generador de KMZ | Estandariza, valida, sin instalar nada, autocontenido | Base no compartida en tiempo real; clave no es seguridad real |
| Motor QGIS | Reutiliza QGIS ya conocido; lógica de conflictos automática | Manual; ruta fija; aproximación en metros |
| Dashboard | Filtros potentes, línea de tiempo, PDF, marca EPM | Datos estáticos; depende de re-correr y subir |
| Mantenimiento | Todo en archivos de texto, fácil de versionar en Git | Coordinación manual entre las tres piezas |

---

## 9. Posibilidades de mejora y potencial a ajustar
- **Base compartida real** para `contratos_db.json` (hoja de cálculo en la nube, pequeño backend o API con autenticación) en lugar de exportar/subir a mano.
- **Municipio automático por geometría** (cruce punto-en-polígono con límites municipales) en vez de selección manual.
- **Categoría propia de "ingreso y salida"** en la leyenda del dashboard/mapa.
- **Automatizar** la corrida de QGIS + exportación qgis2web (PyQGIS headless o tarea programada) para refrescar sin pasos manuales.
- **Soporte de varios proyectos por contrato** y de **polígonos**.
- **Edición de geometría** (mover vértices) dentro del generador.
- **Validación de códigos de contrato** contra un maestro externo y **bitácora** de quién generó cada KMZ.
- Migrar de **CSV a base de datos o API** para escalar.
- **Datos en vivo** en el dashboard (que se actualice al subir el CSV sin recargar manual).
- **SEGURIDAD** (sección 10): control de acceso real.

---

## 10. SEGURIDAD — workstream de autenticación (pendiente prioritario)
**Objetivo pedido:** que solo entren funcionarios de EPM (correo `@epm.com.co`) mediante un **código de un solo uso que cambia en cada acceso (OTP)** enviado a su correo.

**Punto clave:** un sitio estático en GitHub Pages **no puede autenticar ni proteger los datos** por sí solo (una "puerta" en JavaScript no impide descargar el CSV directo). Se requiere: (1) un **dominio propio** y (2) apoyarse en un servicio de autenticación, poniendo el sitio **detrás de una puerta que controle la entrega de los archivos**.

**Dos rutas evaluadas (datos verificados en su momento):**
- **A) Cloudflare Access con "One-time PIN":** envía un PIN de un solo uso al correo aprobado; cada PIN es de un solo uso y al pedir uno nuevo se invalida el anterior; se debe emparejar con el dominio `@epm.com.co`. Requiere gestionar el dominio en Cloudflare y servir el sitio detrás de Cloudflare (p. ej. **Cloudflare Pages**, gratuito). Es lo más cercano a lo pedido y de bajo código. Ojo: las herramientas de seguridad de correo corporativo a veces "consumen" el código antes que el usuario.
- **B) Microsoft Entra ID (Azure Static Web Apps):** inicio de sesión con la **cuenta corporativa** (con MFA), sin códigos que administrar. La restricción al tenant de EPM requiere el **plan Standard (de pago)**; el gratuito no restringe por tenant. Requiere que TI registre la aplicación y dé consentimiento de administrador.

**No hacer:** armar el envío de códigos con una llave de correo incrustada en el HTML (quedaría pública). El envío/validación deben ocurrir en un servicio, nunca en el navegador.

**Recomendación:** involucrar desde el inicio a **TI/Seguridad de EPM** (política de identidad, dominio propio, gobierno de datos). **Pendiente por definir:** si hay dominio propio disponible y si TI apoyaría el registro en Entra ID. Mientras tanto, se puede **ocultar la URL** con el interruptor de GitHub Pages (ver sección 11).

---

## 11. Operación (publicar / ocultar / rutas)
- **Publicar/actualizar:** copiar los archivos a la carpeta del repo → GitHub Desktop → Commit → Push. Recargar con **Ctrl+F5**.
- **Ocultar la plataforma temporalmente:** GitHub → Settings → Pages → botón **Unpublish site** (la URL pasa a 404). **NO** usar la "Danger Zone" ni cambiar la visibilidad del repositorio (eso desconfigura Pages).
- **Volver a mostrarla:** Settings → Pages → Source: *Deploy from a branch → main → /(root)* → Save (1–2 min).
- **CSV al día:** tras correr QGIS, hacer Commit + Push del `reporte_dinamico.csv` para que el dashboard publicado muestre los datos nuevos.
- **Editar siempre por GitHub Desktop** desde el clon en `C:`, nunca por la web en paralelo.

---

## 12. Historial de fases ejecutadas
1. Diseño e implementación del **Generador de KMZ** + documento de análisis con 3 alternativas (numeral 4).
2. **Integración al dashboard** con un botón (una línea, sin afectar nada).
3. **Estabilización de rutas:** repo movido de OneDrive a `C:`, corrección de `HOME`/unidad `U:`, re-clonación, variable única `BASE`.
4. **Municipios múltiples** por contrato en el generador.
5. Opción **"ingreso y salida"** en tipo de cierre + **clave de administrador**.
6. **Puntos azules** de "ingreso y salida" en el motor QGIS.
7. **Filtro Municipio** en el dashboard (facetas cruzadas).
8. Corrección: la lista de tipo de cierre ya **no se cachea** en el navegador.
9. Corrección: **guardar una línea dibujada** aunque no se cierre con doble-clic.
10. **Recuperación de GitHub Pages** tras desconfigurarse por cambio de visibilidad; interruptor seguro publicar/ocultar.
11. **Renombrado** `Plataforma.html` → `Plataforma_PMTs.html`.
12. Definición del pendiente **SEGURIDAD** (autenticación OTP por correo).

---

## 13. Cómo continuar en un Proyecto de Claude y en Claude Code

### 13.1 Instrucciones del Proyecto (bloque para copiar en el Proyecto de Claude)
> Pega esto en "Instrucciones" del Proyecto:

```
Eres mi copiloto técnico para la "Plataforma de Control y Articulación de PMTs" de Grupo EPM.
No soy programadora: explícame todo en lenguaje sencillo y dime qué archivo cambias y por qué.
Responde en español. Antes de recomendar, investiga en la web el estado actual (no confíes solo en memoria).
Usa todo tu potencial: audita el código, propón e implementa mejoras alineadas al objetivo, y usa los
skills que apliquen. Verifica siempre lo que produces (sintaxis, casos de prueba, sin romper lo existente)
antes de decir "listo", y deja los archivos listos para copiar/pegar y subir con GitHub Desktop.
Respeta los invariantes: formato de Descripción del KMZ, lista cerrada de tipo_cierre, columnas del CSV,
nombres de capas de QGIS y marca EPM. No incrustes llaves/secretos en código de cliente ni prometas
seguridad que un sitio estático no da. No hagas cambios destructivos sin explicarlos y pedir confirmación.
El pendiente prioritario es SEGURIDAD (autenticación OTP para correos @epm.com.co).
Todo el contexto está en el archivo DOCUMENTACION_Plataforma_PMTs_EPM.md que cargué como conocimiento.
```

### 13.2 Prompts iniciales sugeridos
- "Léete el documento maestro y el CLAUDE.md y hazme un resumen de cómo entiendes el sistema y sus riesgos."
- "Audita `Generador_KMZ.html` y dime errores, riesgos y 5 mejoras priorizadas, sin cambiar nada aún."
- "Retomemos SEGURIDAD: investiga el estado actual de Cloudflare Access One-time PIN y Azure Entra ID y propónme un plan paso a paso adaptado a EPM."

---

## Anexo A — Código definitivo de los archivos
> Versiones finales de esta fase, incluidas textualmente para que el documento sea autocontenido.

### A.1 — Generador_KMZ.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Generador de KMZ Estandarizado — PMTs EPM</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>

<style>
  :root{ --epm-verde:#009300; --epm-lima:#b7c200; --epm-naranja:#d56b00; }
  body{ background:#f8f9fa; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; }
  .epm-header{ background:#fff; border-bottom:4px solid var(--epm-verde); box-shadow:0 2px 8px rgba(0,0,0,.1); padding:10px 20px; }
  .epm-title{ color:var(--epm-verde); font-weight:bold; font-size:19px; margin-left:12px; vertical-align:middle; }
  .card-head{ background:var(--epm-verde); color:#fff; font-weight:bold; padding:8px 14px; font-size:.95rem; border-radius:6px 6px 0 0; display:flex; justify-content:space-between; align-items:center;}
  .card-box{ background:#fff; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,.08); margin-bottom:16px; overflow:hidden; }
  .card-body2{ padding:14px 16px; }
  .epm-btn{ background:var(--epm-lima); color:#000; font-weight:bold; border:none; }
  .epm-btn:hover{ background:#99a800; }
  .epm-btn-green{ background:var(--epm-verde); color:#fff; font-weight:bold; border:none;}
  .epm-btn-green:hover{ background:#007a00; color:#fff;}
  .epm-btn-orange{ background:var(--epm-naranja); color:#fff; font-weight:bold; border:none;}
  #map{ height:380px; border:3px solid var(--epm-verde); border-radius:8px; }
  .badge-ok{ background:var(--epm-verde);} .badge-warn{ background:var(--epm-naranja);} .badge-bad{ background:#dc3545;}
  table td, table th{ font-size:.82rem; vertical-align:middle;}
  .req-label{ font-weight:600; font-size:.8rem; color:#333;}
  .mini{ font-size:.72rem; color:#6c757d;}
  .step-num{ display:inline-block; width:24px; height:24px; line-height:24px; text-align:center; border-radius:50%; background:var(--epm-verde); color:#fff; font-weight:bold; font-size:.8rem; margin-right:6px;}
  .auto-field{ background:#eef7ee !important; }
  .drawing-hint{ position:absolute; z-index:500; top:8px; left:50px; background:rgba(0,0,0,.7); color:#fff; padding:4px 10px; border-radius:6px; font-size:.78rem; display:none;}
</style>
</head>
<body>

<div class="epm-header d-flex align-items-center">
  <span style="font-size:26px">🛠️</span>
  <span class="epm-title">GENERADOR DE KMZ ESTANDARIZADO — PMTs</span>
  <span class="ms-auto mini">Grupo EPM · Centro de Gestión Servicios Técnicos</span>
</div>

<div class="container-fluid p-3">
  <div class="alert alert-light border mb-3" style="border-left:5px solid var(--epm-lima)!important">
    <b>¿Qué hace esta herramienta?</b> Elimina la escritura manual del campo <i>Descripción</i> del KMZ.
    El usuario dibuja o importa la geometría y elige los datos en menús validados; la herramienta arma el texto
    con el formato exacto que exige el motor de análisis y descarga un <b>.kmz listo para la carpeta de entrada</b>.
  </div>

  <div class="row">
    <!-- ================= COLUMNA IZQUIERDA ================= -->
    <div class="col-lg-7">

      <!-- PASO 1: BASE DE DATOS MAESTRA -->
      <div class="card-box">
        <div class="card-head"><span><span class="step-num">1</span>Base de datos maestra (la administra el gestor de la plataforma)</span>
          <div>
            <button id="btnLock" class="btn btn-sm btn-warning fw-bold" onclick="toggleLock()">🔒 Desbloquear edición</button>
            <button id="btnImportDB" class="btn btn-sm btn-light" onclick="importarDB()" disabled>📥 Importar JSON</button>
            <button class="btn btn-sm btn-light" onclick="exportarDB()">💾 Exportar JSON</button>
          </div>
        </div>
        <div class="card-body2">
          <p class="mini mb-2">Aquí se registran una sola vez los valores que <b>deben repetirse idénticos</b>: contrato → contratista y proyecto.
          Un contrato puede tener <b>varios municipios</b> (sepáralos con <code>;</code>): al crear cada trazado se elige el municipio de un menú. El usuario nunca los escribe: los selecciona.
          <b>🔒 La edición está protegida con clave de administrador EPM</b> para mantener uniformidad (p. ej. un mismo contratista en varios contratos debe escribirse igual). Guarda el JSON exportado como <code>contratos_db.json</code> en el repositorio para conservarlo.</p>
          <div class="table-responsive" style="max-height:200px; overflow:auto">
            <table class="table table-sm table-striped mb-2">
              <thead class="table-dark"><tr><th>Contrato</th><th>Contratista</th><th>Proyecto</th><th>Municipio</th><th></th></tr></thead>
              <tbody id="dbBody"></tbody>
            </table>
          </div>
          <div class="row g-1">
            <div class="col"><input id="nCon" class="form-control form-control-sm" placeholder="Contrato (ej: CW323402)"></div>
            <div class="col"><input id="nContr" class="form-control form-control-sm" placeholder="Contratista"></div>
            <div class="col"><input id="nProy" class="form-control form-control-sm" placeholder="Proyecto"></div>
            <div class="col"><input id="nMun" class="form-control form-control-sm" placeholder="Municipio(s) — separa con ;"></div>
            <div class="col-auto"><button id="btnAddDB" class="btn btn-sm epm-btn-green" onclick="addDB()" disabled>+ Agregar</button></div>
          </div>
        </div>
      </div>

      <!-- PASO 2: GEOMETRIA -->
      <div class="card-box">
        <div class="card-head"><span><span class="step-num">2</span>Geometría del trazado</span></div>
        <div class="card-body2">
          <div class="d-flex flex-wrap gap-2 mb-2">
            <label class="btn btn-sm epm-btn mb-0">📂 Importar KMZ/KML de Google Earth
              <input type="file" accept=".kmz,.kml" onchange="importarGeom(this.files[0])" hidden></label>
            <button class="btn btn-sm epm-btn-green" onclick="modoDibujo('linea')">✏️ Dibujar línea</button>
            <button class="btn btn-sm epm-btn-green" onclick="modoDibujo('punto')">📍 Colocar punto</button>
            <button class="btn btn-sm btn-outline-secondary" onclick="cancelarDibujo()">✖ Cancelar dibujo</button>
          </div>
          <div style="position:relative">
            <div id="hint" class="drawing-hint"></div>
            <div id="map"></div>
          </div>
          <p class="mini mt-2">Al <b>importar</b>, si el KMZ ya trae datos en la descripción, la herramienta los lee y precarga el formulario para que solo revises y corrijas. Al <b>dibujar</b>: clic para agregar vértices y doble-clic para terminar la línea.</p>
        </div>
      </div>
    </div>

    <!-- ================= COLUMNA DERECHA ================= -->
    <div class="col-lg-5">

      <!-- PASO 3: FORMULARIO VALIDADO -->
      <div class="card-box">
        <div class="card-head"><span><span class="step-num">3</span>Datos del trazado (menús validados)</span></div>
        <div class="card-body2">
          <div class="mb-2">
            <label class="req-label">Nombre del frente *</label>
            <div class="input-group input-group-sm">
              <input id="fNombre" class="form-control form-control-sm" placeholder="Ej: PMT_01_01">
              <button class="btn epm-btn" onclick="sugerirNombre()" title="Sugerir siguiente consecutivo">↻</button>
            </div>
          </div>
          <div class="mb-2">
            <label class="req-label">Contrato *</label>
            <select id="fContrato" class="form-select form-select-sm" onchange="autoLlenar()"></select>
          </div>
          <div class="row g-1 mb-2">
            <div class="col"><label class="req-label">Contratista</label><input id="fContratista" class="form-control form-control-sm auto-field" readonly></div>
          </div>
          <div class="row g-1 mb-2">
            <div class="col"><label class="req-label">Proyecto</label><input id="fProyecto" class="form-control form-control-sm auto-field" readonly></div>
            <div class="col"><label class="req-label">Municipio *</label><select id="fMunicipio" class="form-select form-select-sm"></select></div>
          </div>
          <div class="mb-2">
            <label class="req-label">Tipo de cierre *</label>
            <select id="fTipoCierre" class="form-select form-select-sm"></select>
            <span class="mini">Lista cerrada (total, parcial, ingreso y salida). En el mapa: <b>total</b> rojo y <b>parcial</b> amarillo; <b>ingreso y salida</b> se clasifica como "Otros".</span>
          </div>
          <div class="row g-1 mb-2">
            <div class="col"><label class="req-label">Fecha y hora inicio *</label><input id="fInicio" type="datetime-local" class="form-control form-control-sm"></div>
            <div class="col"><label class="req-label">Fecha y hora fin *</label><input id="fFin" type="datetime-local" class="form-control form-control-sm"></div>
          </div>
          <div class="mb-2">
            <label class="req-label">Dirección *</label>
            <input id="fDireccion" class="form-control form-control-sm" placeholder="Texto libre (no usar el carácter | )">
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm epm-btn-green flex-grow-1" onclick="guardarTrazado()">💾 Guardar / Actualizar trazado</button>
            <button class="btn btn-sm epm-btn" onclick="limpiarForm()">Nuevo</button>
          </div>
          <div id="editHint" class="mini mt-1 text-danger"></div>
        </div>
      </div>

      <!-- PASO 5: EXPORTAR -->
      <div class="card-box">
        <div class="card-head"><span><span class="step-num">5</span>Validar y exportar</span></div>
        <div class="card-body2">
          <div id="validBox" class="mini mb-2">Aún no hay trazados cargados.</div>
          <button class="btn epm-btn-green w-100 fw-bold" onclick="exportarKMZ()">⬇️ Generar y descargar KMZ estandarizado</button>
        </div>
      </div>
    </div>
  </div>

  <!-- PASO 4: LISTA DE TRAZADOS -->
  <div class="card-box">
    <div class="card-head"><span><span class="step-num">4</span>Trazados en este KMZ</span>
      <span class="mini text-white">Total: <span id="cnt">0</span></span></div>
    <div class="card-body2">
      <div class="table-responsive">
        <table class="table table-sm table-hover">
          <thead class="table-dark"><tr>
            <th>#</th><th>Frente</th><th>Tipo geom.</th><th>Contrato</th><th>Cierre</th><th>Inicio</th><th>Fin</th><th>Estado</th><th>Acciones</th>
          </tr></thead>
          <tbody id="listaBody"><tr><td colspan="9" class="text-center mini py-3">Sin trazados todavía.</td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
/* ============================================================
   GENERADOR DE KMZ ESTANDARIZADO — PMTs EPM
   Autocontenido. Depende de Leaflet (mapa) y JSZip (empaquetado).
   ============================================================ */

/* ---------- Estado global ---------- */
let DB = [];                 // base maestra: {contrato, contratista, proyecto, municipio}
let TIPOS_CIERRE = ['total','parcial','ingreso y salida'];   // lista cerrada configurable
let trazados = [];           // {id, nombre, geomType, coords:[[lat,lng],...], contrato, contratista, proyecto, municipio, tipo, inicio, fin, direccion}
let editandoId = null;
let idSeq = 1;

/* ---------- Control de acceso a la Base maestra (solo personal EPM) ---------- */
let dbUnlocked = false;
// SHA-256 de la clave. Clave por defecto: EPM-PMT-2026  (ver instrucciones para cambiarla)
const CLAVE_HASH = "144887dea6c6f4df6d7341dd219576dce28dd3a0adb5398fd1a1c2bc577cd200";
async function sha256(txt){
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt));
  return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('');
}
async function toggleLock(){
  if(dbUnlocked){ dbUnlocked=false; aplicarLock(); return; }
  const k = prompt('Clave de administrador EPM para editar la base de datos:');
  if(k===null) return;
  try{
    const h = await sha256(k);
    if(h===CLAVE_HASH){ dbUnlocked=true; aplicarLock(); }
    else alert('Clave incorrecta.');
  }catch(e){ alert('Este navegador no permite validar la clave (requiere HTTPS/GitHub Pages).'); }
}
function aplicarLock(){
  const btn=document.getElementById('btnLock');
  btn.textContent = dbUnlocked? '🔓 Bloquear edición' : '🔒 Desbloquear edición';
  btn.className   = 'btn btn-sm fw-bold '+(dbUnlocked?'btn-success':'btn-warning');
  ['btnImportDB','btnAddDB','nCon','nContr','nProy','nMun'].forEach(id=>{ const el=document.getElementById(id); if(el) el.disabled=!dbUnlocked; });
  renderDB(); // re-dibuja para mostrar/ocultar botones de borrar
}

/* ---------- Semilla de base maestra (ejemplos reales del contexto) ---------- */
const DB_SEED = [
  {contrato:'CW323402', contratista:'CONSORCIO_INFRAESTRUCTURA_DE_AGUAS_2024', proyecto:'ORFELINATO', municipios:['Medellín']},
  {contrato:'CW328120', contratista:'SANEAR S.A.S', proyecto:'EDIE1', municipios:['Medellín']}
];
/* Normaliza la base: garantiza que cada contrato tenga una LISTA de municipios
   (convierte el formato antiguo {municipio:'X'} a {municipios:['X']}) */
function normalizeDB(db){
  return (db||[]).map(r=>{
    let muns = r.municipios;
    if(!Array.isArray(muns)) muns = r.municipio ? [r.municipio] : [];
    muns = muns.map(x=>String(x).trim()).filter(Boolean);
    return {contrato:r.contrato, contratista:r.contratista, proyecto:r.proyecto, municipios:muns};
  });
}
function splitMunicipios(txt){ return String(txt||'').split(/[;,]/).map(s=>s.trim()).filter(Boolean); }
function municipiosDe(contrato){ const r=DB.find(x=>x.contrato===contrato); return r? (r.municipios||[]) : []; }

/* ---------- Persistencia suave (localStorage con try/catch) ----------
   Solo se persiste la base de contratos (pmt_db). La lista de tipos de cierre
   es un valor canónico del código y NO se cachea, para que siempre gane la
   versión del archivo (evita que una lista antigua guardada la sobrescriba). */
function guardarLocal(){ try{ localStorage.setItem('pmt_db', JSON.stringify(DB)); }catch(e){} }
function cargarLocal(){
  try{
    const d = localStorage.getItem('pmt_db'); if(d) DB = JSON.parse(d);
    localStorage.removeItem('pmt_tipos'); // limpia cualquier lista antigua cacheada
  }catch(e){}
}

/* ---------- Arranque ---------- */
async function init(){
  cargarLocal();
  if(!DB.length){
    // Intento cargar contratos_db.json si el archivo está publicado junto al HTML
    try{
      const r = await fetch('contratos_db.json',{cache:'no-store'});
      if(r.ok){ DB = await r.json(); }
    }catch(e){}
  }
  if(!DB.length) DB = JSON.parse(JSON.stringify(DB_SEED));
  DB = normalizeDB(DB);
  renderDB(); renderTiposCierre(); renderContratoSelect(); renderLista(); validar();
  aplicarLock();  // arranca con la base bloqueada
  initMapa();
}

/* ===========================================================
   BASE DE DATOS MAESTRA
   =========================================================== */
function renderDB(){
  const b = document.getElementById('dbBody'); b.innerHTML='';
  DB.forEach((r,i)=>{
    b.innerHTML += `<tr>
      <td>${esc(r.contrato)}</td><td>${esc(r.contratista)}</td><td>${esc(r.proyecto)}</td><td>${esc((r.municipios||[]).join('; '))}</td>
      <td>${dbUnlocked ? `<button class="btn btn-sm btn-outline-danger py-0" onclick="delDB(${i})">🗑</button>` : '<span class="mini">🔒</span>'}</td></tr>`;
  });
  guardarLocal();
}
function addDB(){
  if(!dbUnlocked){ alert('Debes desbloquear la edición con la clave de administrador EPM.'); return; }
  const c=val('nCon').trim().toUpperCase(), ct=val('nContr').trim(), p=val('nProy').trim();
  const muns=splitMunicipios(val('nMun'));
  if(!c || !ct || !p){ alert('Contrato, contratista y proyecto son obligatorios en la base.'); return; }
  const ex = DB.find(x=>x.contrato===c);
  if(ex){
    // Mismo contrato: NO se duplica la fila; se agregan los municipios nuevos a su lista.
    let nuevos=0; muns.forEach(mn=>{ if(mn && !ex.municipios.includes(mn)){ ex.municipios.push(mn); nuevos++; } });
    alert('El contrato '+c+' ya existía. Se añadieron '+nuevos+' municipio(s) a su lista.');
  } else {
    DB.push({contrato:c, contratista:ct, proyecto:p, municipios:muns});
  }
  ['nCon','nContr','nProy','nMun'].forEach(id=>document.getElementById(id).value='');
  renderDB(); renderContratoSelect();
}
function delDB(i){ if(!dbUnlocked){ alert('Debes desbloquear la edición con la clave.'); return; } if(confirm('¿Eliminar '+DB[i].contrato+' de la base?')){ DB.splice(i,1); renderDB(); renderContratoSelect(); } }
function exportarDB(){ descargar(JSON.stringify(DB,null,2), 'contratos_db.json', 'application/json'); }
function importarDB(){
  if(!dbUnlocked){ alert('Debes desbloquear la edición con la clave.'); return; }
  const inp=document.createElement('input'); inp.type='file'; inp.accept='.json';
  inp.onchange=e=>{ const f=e.target.files[0]; const rd=new FileReader();
    rd.onload=()=>{ try{ DB=normalizeDB(JSON.parse(rd.result)); renderDB(); renderContratoSelect(); alert('Base cargada: '+DB.length+' contratos.'); }catch(err){ alert('JSON inválido.'); } };
    rd.readAsText(f); };
  inp.click();
}

/* ===========================================================
   SELECTS VALIDADOS
   =========================================================== */
function renderContratoSelect(){
  const s=document.getElementById('fContrato'); const prev=s.value;
  s.innerHTML='<option value="">— Seleccione contrato —</option>';
  DB.forEach(r=> s.innerHTML+=`<option value="${esc(r.contrato)}">${esc(r.contrato)}</option>`);
  if(prev) s.value=prev; autoLlenar();
}
function renderTiposCierre(){
  const s=document.getElementById('fTipoCierre');
  s.innerHTML='<option value="">— Seleccione —</option>';
  TIPOS_CIERRE.forEach(t=> s.innerHTML+=`<option value="${esc(t)}">${esc(t)}</option>`);
}
function autoLlenar(municipioSel){
  const c=val('fContrato'); const r=DB.find(x=>x.contrato===c);
  document.getElementById('fContratista').value = r? r.contratista : '';
  document.getElementById('fProyecto').value    = r? r.proyecto    : '';
  llenarMunicipios(r? r.municipios : [], municipioSel);
}
/* Construye el menú de municipios del contrato elegido.
   - 1 municipio  -> se selecciona solo.
   - varios       -> muestra "Seleccione" para forzar elección consciente.
   - 'sel' conserva un municipio importado aunque no esté en la base. */
function llenarMunicipios(lista, sel){
  const s=document.getElementById('fMunicipio');
  const arr=(lista||[]).slice();
  if(sel && !arr.includes(sel)) arr.push(sel);
  let html='';
  if(arr.length!==1) html+='<option value="">— Seleccione municipio —</option>';
  arr.forEach(m=> html+=`<option value="${esc(m)}">${esc(m)}</option>`);
  s.innerHTML=html;
  if(sel) s.value=sel; else if(arr.length===1) s.value=arr[0];
}

/* ===========================================================
   MAPA (Leaflet) + DIBUJO
   =========================================================== */
let map, capaTrazados, dibujoModo=null, dibujoTemp=[], dibujoLayer=null;
function initMapa(){
  map = L.map('map').setView([6.2612, -75.5722], 15); // centrado en zona del ejemplo
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19, attribution:'© OpenStreetMap'}).addTo(map);
  capaTrazados = L.layerGroup().addTo(map);
  map.on('click', onMapClick);
  map.on('dblclick', onMapDbl);
}
function modoDibujo(tipo){
  dibujoModo=tipo; dibujoTemp=[];
  if(dibujoLayer){ map.removeLayer(dibujoLayer); dibujoLayer=null; }
  const h=document.getElementById('hint'); h.style.display='block';
  h.textContent = tipo==='linea' ? 'Modo LÍNEA: clic para vértices, doble-clic para terminar.' : 'Modo PUNTO: clic para colocar el punto.';
  if(tipo==='linea') map.doubleClickZoom.disable();
}
function cancelarDibujo(){ dibujoModo=null; dibujoTemp=[]; if(dibujoLayer){map.removeLayer(dibujoLayer);dibujoLayer=null;} document.getElementById('hint').style.display='none'; map.doubleClickZoom.enable(); }
function onMapClick(e){
  if(!dibujoModo) return;
  if(dibujoModo==='punto'){
    finalizarGeom('Point', [[e.latlng.lat, e.latlng.lng]]);
    cancelarDibujo(); return;
  }
  dibujoTemp.push([e.latlng.lat, e.latlng.lng]);
  if(dibujoLayer) map.removeLayer(dibujoLayer);
  dibujoLayer = L.polyline(dibujoTemp,{color:'#d56b00',weight:5}).addTo(map);
}
function onMapDbl(e){
  if(dibujoModo!=='linea') return;
  if(dibujoTemp.length>=2){ finalizarGeom('LineString', dibujoTemp.slice()); }
  cancelarDibujo();
}
function finalizarGeom(tipo, coords){
  // Crea un trazado nuevo con la geometría; los datos se completan en el formulario
  const t = nuevoTrazadoVacio(); t.geomType=tipo; t.coords=coords;
  trazados.push(t); editandoId=t.id; cargarEnForm(t);
  renderLista(); dibujarTodo(); validar();
  document.getElementById('editHint').textContent='Geometría dibujada. Completa los datos y presiona "Guardar / Actualizar".';
}

/* ===========================================================
   IMPORTAR KMZ / KML  (lee geometría y precarga descripción)
   =========================================================== */
async function importarGeom(file){
  if(!file) return;
  let kmlText='';
  try{
    if(file.name.toLowerCase().endsWith('.kmz')){
      const zip = await JSZip.loadAsync(file);
      const kmlName = Object.keys(zip.files).find(n=>n.toLowerCase().endsWith('.kml'));
      if(!kmlName){ alert('El KMZ no contiene un .kml'); return; }
      kmlText = await zip.files[kmlName].async('string');
    }else{
      kmlText = await file.text();
    }
  }catch(e){ alert('No se pudo leer el archivo: '+e.message); return; }

  const dom = new DOMParser().parseFromString(kmlText, 'text/xml');
  const placemarks = getByLocal(dom, 'Placemark');
  if(!placemarks.length){ alert('No se encontraron trazados (Placemark) en el archivo.'); return; }

  let importados=0;
  placemarks.forEach(pm=>{
    const nombre = textLocal(pm,'name') || 'SIN_NOMBRE';
    const desc   = textLocal(pm,'description') || '';
    const meta   = parseDescripcion(desc);   // intenta leer el formato existente

    // Geometría
    let geomType=null, coords=[];
    const ls = getByLocal(pm,'LineString')[0];
    const pt = getByLocal(pm,'Point')[0];
    if(ls){ geomType='LineString'; coords = parseCoords(textLocal(ls,'coordinates')); }
    else if(pt){ geomType='Point'; coords = parseCoords(textLocal(pt,'coordinates')); }
    else return; // ignora polígonos u otros por ahora

    // Empareja contrato con la base para auto-completar (si existe)
    const enBase = DB.find(x=>x.contrato===(meta.contrato||'').toUpperCase());
    const t = nuevoTrazadoVacio();
    t.nombre = nombre; t.geomType=geomType; t.coords=coords;
    t.contrato   = (meta.contrato||'').toUpperCase();
    t.contratista= enBase? enBase.contratista : (meta.contratista||'');
    t.proyecto   = enBase? enBase.proyecto    : (meta.proyecto||'');
    // municipio: prioriza el del KMZ; si no viene y el contrato tiene un único municipio, lo asume
    t.municipio  = (meta.municipio||'').trim() || (enBase && (enBase.municipios||[]).length===1 ? enBase.municipios[0] : '');
    t.tipo       = normalizarTipo(meta.tipo_cierre||'');
    t.inicio     = normalizarFechaEntrada(meta.fecha_inicio||'');
    t.fin        = normalizarFechaEntrada(meta.fecha_fin||'');
    t.direccion  = (meta.direccion||'').replace(/\|/g,'/');
    trazados.push(t); importados++;
  });
  renderLista(); dibujarTodo(); validar(); ajustarVista();
  alert(importados+' trazado(s) importado(s). Revisa cada uno en la tabla y corrige lo que falte (aparecen marcados si tienen datos incompletos).');
}

/* ===========================================================
   FORMULARIO ↔ TRAZADO
   =========================================================== */
function nuevoTrazadoVacio(){
  return {id:idSeq++, nombre:'', geomType:null, coords:[], contrato:'', contratista:'', proyecto:'', municipio:'', tipo:'', inicio:'', fin:'', direccion:''};
}
function cargarEnForm(t){
  editandoId=t.id;
  set('fNombre',t.nombre); set('fContrato',t.contrato);
  autoLlenar(t.municipio);   // arma el menú de municipios y selecciona el del trazado
  // si el contrato no estaba en la base, respeta contratista/proyecto importados
  if(!DB.find(x=>x.contrato===t.contrato)){ set('fContratista',t.contratista); set('fProyecto',t.proyecto); }
  set('fTipoCierre',t.tipo); set('fInicio',aInputDateTime(t.inicio)); set('fFin',aInputDateTime(t.fin)); set('fDireccion',t.direccion);
  document.getElementById('editHint').textContent='Editando: '+(t.nombre||'(sin nombre)');
}
function guardarTrazado(){
  let t = trazados.find(x=>x.id===editandoId);
  if(!t){ t=nuevoTrazadoVacio(); trazados.push(t); editandoId=t.id; }
  t.nombre    = val('fNombre').trim();
  t.contrato  = val('fContrato');
  t.contratista = val('fContratista').trim();
  t.proyecto  = val('fProyecto').trim();
  t.municipio = val('fMunicipio').trim();
  t.tipo      = val('fTipoCierre');
  t.inicio    = deInputDateTime(val('fInicio'));
  t.fin       = deInputDateTime(val('fFin'));
  t.direccion = val('fDireccion').trim().replace(/\|/g,'/');  // protege el separador
  // Si hay un dibujo en curso SIN finalizar (no se hizo doble-clic), se toma como geometría.
  // El doble-clic sigue funcionando igual; esto solo añade una vía alterna para no perder el trazo.
  if(!t.geomType && dibujoTemp.length){
    if(dibujoModo==='linea' && dibujoTemp.length>=2){ t.geomType='LineString'; t.coords=dibujoTemp.slice(); cancelarDibujo(); }
    else if(dibujoModo==='punto'){ t.geomType='Point'; t.coords=[dibujoTemp[0]]; cancelarDibujo(); }
  }
  if(!t.geomType){ alert('Este trazado no tiene geometría. Dibuja la línea (un clic por vértice) o importa primero.'); return; }
  renderLista(); dibujarTodo(); validar();
  document.getElementById('editHint').textContent='Guardado ✔';
}
function limpiarForm(){
  editandoId=null;
  ['fNombre','fContratista','fProyecto','fMunicipio','fInicio','fFin','fDireccion'].forEach(id=>set(id,''));
  set('fContrato',''); set('fTipoCierre','');
  autoLlenar();  // limpia el menú de municipios
  document.getElementById('editHint').textContent='';
}
function sugerirNombre(){
  // Sugere PMT_01_XX incrementando el mayor consecutivo existente
  let max=0;
  trazados.forEach(t=>{ const m=(t.nombre||'').match(/(\d+)\s*$/); if(m) max=Math.max(max, parseInt(m[1])); });
  const n=String(max+1).padStart(2,'0');
  set('fNombre','PMT_01_'+n);
}

/* ===========================================================
   DUPLICAR PARA NUEVA VIGENCIA
   =========================================================== */
function duplicarVigencia(id){
  const o = trazados.find(x=>x.id===id); if(!o) return;
  const c = JSON.parse(JSON.stringify(o)); c.id=idSeq++;
  c.inicio=''; c.fin='';           // solo cambian las fechas
  trazados.push(c); cargarEnForm(c);
  renderLista(); validar();
  document.getElementById('editHint').textContent='Copia creada para nueva vigencia: cambia solo las fechas y guarda.';
  window.scrollTo({top:0, behavior:'smooth'});
}
function editar(id){ const t=trazados.find(x=>x.id===id); if(t){ cargarEnForm(t); window.scrollTo({top:0,behavior:'smooth'}); } }
function borrar(id){ trazados=trazados.filter(x=>x.id!==id); if(editandoId===id) limpiarForm(); renderLista(); dibujarTodo(); validar(); }

/* ===========================================================
   LISTA + VALIDACIÓN
   =========================================================== */
function faltantes(t){
  const f=[];
  if(!t.nombre) f.push('nombre'); if(!t.contrato) f.push('contrato');
  if(!t.tipo) f.push('tipo_cierre'); if(!t.inicio) f.push('fecha_inicio');
  if(!t.fin) f.push('fecha_fin'); if(!t.direccion) f.push('direccion');
  if(!t.geomType) f.push('geometría');
  if(t.inicio && t.fin && t.fin < t.inicio) f.push('fin<inicio');
  const rc=DB.find(x=>x.contrato===t.contrato);
  if(rc && (rc.municipios||[]).length && !t.municipio) f.push('municipio');
  return f;
}
function renderLista(){
  const b=document.getElementById('listaBody'); document.getElementById('cnt').textContent=trazados.length;
  if(!trazados.length){ b.innerHTML='<tr><td colspan="9" class="text-center mini py-3">Sin trazados todavía.</td></tr>'; return; }
  b.innerHTML='';
  trazados.forEach((t,i)=>{
    const f=faltantes(t);
    const estado = f.length ? `<span class="badge badge-bad">Falta: ${f.join(', ')}</span>` : `<span class="badge badge-ok">Completo</span>`;
    b.innerHTML += `<tr>
      <td>${i+1}</td><td>${esc(t.nombre)||'<i class="mini">—</i>'}</td><td>${t.geomType==='Point'?'Punto':'Línea'}</td>
      <td>${esc(t.contrato)}</td><td>${esc(t.tipo)}</td><td>${esc(t.inicio)}</td><td>${esc(t.fin)}</td><td>${estado}</td>
      <td style="white-space:nowrap">
        <button class="btn btn-sm epm-btn py-0" onclick="editar(${t.id})" title="Editar">✏️</button>
        <button class="btn btn-sm epm-btn-orange py-0" onclick="duplicarVigencia(${t.id})" title="Duplicar para nueva vigencia">🗓️+</button>
        <button class="btn btn-sm btn-outline-danger py-0" onclick="borrar(${t.id})" title="Eliminar">🗑</button>
      </td></tr>`;
  });
}
function validar(){
  const box=document.getElementById('validBox');
  if(!trazados.length){ box.innerHTML='Aún no hay trazados cargados.'; return; }
  const malos=trazados.filter(t=>faltantes(t).length);
  if(malos.length){ box.innerHTML=`<span class="badge badge-bad">${malos.length}</span> trazado(s) con datos incompletos. Corrígelos antes de exportar.`; }
  else{ box.innerHTML=`<span class="badge badge-ok">OK</span> ${trazados.length} trazado(s) completos y válidos. Listo para exportar.`; }
}

/* ===========================================================
   DIBUJAR EN MAPA
   =========================================================== */
function dibujarTodo(){
  if(!capaTrazados) return; capaTrazados.clearLayers();
  trazados.forEach(t=>{
    if(!t.coords||!t.coords.length) return;
    let lyr;
    if(t.geomType==='Point') lyr=L.circleMarker(t.coords[0],{radius:6,color:'#009300',fillColor:'#b7c200',fillOpacity:.9});
    else lyr=L.polyline(t.coords,{color: t.tipo==='total'?'#e31a1c':(t.tipo==='parcial'?'#e6a800':(t.tipo==='ingreso y salida'?'#1f78b4':'#969696')), weight:5});
    lyr.bindTooltip((t.nombre||'(sin nombre)')+' · '+(t.tipo||'sin tipo'));
    lyr.on('click',()=>editar(t.id));
    capaTrazados.addLayer(lyr);
  });
}
function ajustarVista(){
  const pts=[]; trazados.forEach(t=>t.coords.forEach(c=>pts.push(c)));
  if(pts.length) map.fitBounds(L.latLngBounds(pts).pad(0.2));
}

/* ===========================================================
   EXPORTAR KMZ
   =========================================================== */
async function exportarKMZ(){
  if(!trazados.length){ alert('No hay trazados para exportar.'); return; }
  const malos=trazados.filter(t=>faltantes(t).length);
  if(malos.length && !confirm(malos.length+' trazado(s) tienen datos incompletos. ¿Exportar de todos modos?')) return;

  const contrato = (trazados.find(t=>t.contrato)||{}).contrato || 'CONTRATO';
  const proyecto = (trazados.find(t=>t.proyecto)||{}).proyecto || 'PROYECTO';
  const nombreArchivo = `${contrato}_${proyecto}`.replace(/[^A-Za-z0-9_\-]/g,'_')+'.kmz';

  const kml = construirKML(nombreArchivo);
  const zip = new JSZip();
  zip.file('doc.kml', kml);
  const blob = await zip.generateAsync({type:'blob', mimeType:'application/vnd.google-earth.kmz'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=nombreArchivo; a.click();
}
function construirKML(nombreDoc){
  let body='';
  trazados.forEach(t=>{
    const desc = construirDescripcion(t);
    let geom='';
    if(t.geomType==='Point'){
      const c=t.coords[0]; geom=`<Point><coordinates>${c[1]},${c[0]},0</coordinates></Point>`;
    }else{
      const cs=t.coords.map(c=>`${c[1]},${c[0]},0`).join(' ');
      geom=`<LineString><tessellate>1</tessellate><coordinates>${cs}</coordinates></LineString>`;
    }
    body += `<Placemark><name>${esc(t.nombre)}</name><description>${esc(desc)}</description>${geom}</Placemark>\n`;
  });
  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>${esc(nombreDoc)}</name>
${body}</Document></kml>`;
}
/* Construye el string EXACTO que espera el motor de análisis (orden idéntico al de los KMZ actuales) */
function construirDescripcion(t){
  const partes = [
    `fecha_inicio: ${t.inicio}`,
    `fecha_fin: ${t.fin}`,
    `tipo_cierre: ${t.tipo}`,
    `direccion: ${t.direccion}`,
  ];
  if(t.municipio) partes.push(`municipio: ${t.municipio}`);
  partes.push(`contrato: ${t.contrato}`);
  partes.push(`contratista: ${t.contratista}`);
  partes.push(`proyecto: ${t.proyecto}`);
  return partes.join(' | ');
}

/* ===========================================================
   UTILIDADES
   =========================================================== */
function parseDescripcion(desc){
  const campos=['fecha_inicio','fecha_fin','tipo_cierre','direccion','municipio','contrato','contratista','proyecto'];
  const out={};
  campos.forEach(c=>{ const m=desc.match(new RegExp(c+'\\s*:\\s*([^|]+)','i')); if(m) out[c]=m[1].trim(); });
  return out;
}
function normalizarTipo(v){
  const s=(v||'').trim().toLowerCase();
  if(TIPOS_CIERRE.includes(s)) return s;
  // añade a la lista si es un valor nuevo detectado, para no perder el dato
  if(s){ if(!TIPOS_CIERRE.includes(s)){ TIPOS_CIERRE.push(s); renderTiposCierre(); } return s; }
  return '';
}
/* Corrige el clásico 24:00:00 -> 00:00:00 del día siguiente y unifica a 'YYYY-MM-DD HH:MM:SS' */
function normalizarFechaEntrada(raw){
  if(!raw) return '';
  let s=raw.trim();
  const fm=s.match(/(\d{4})-(\d{2})-(\d{2})/); if(!fm) return '';
  let [_, Y,M,D]=fm; let hh='00',mm='00',ss='00';
  const hm=s.match(/(\d{1,2}):(\d{2})(?::(\d{2}))?/);
  if(hm){ hh=hm[1].padStart(2,'0'); mm=hm[2]; ss=hm[3]||'00'; }
  if(parseInt(hh)>=24){ // 24:00 -> día siguiente 00:00
    const d=new Date(Date.UTC(+Y,+M-1,+D)); d.setUTCDate(d.getUTCDate()+1);
    Y=d.getUTCFullYear(); M=String(d.getUTCMonth()+1).padStart(2,'0'); D=String(d.getUTCDate()).padStart(2,'0');
    hh='00'; mm='00'; ss='00';
  }
  return `${Y}-${M}-${D} ${hh}:${mm}:${ss}`;
}
function aInputDateTime(s){ // 'YYYY-MM-DD HH:MM:SS' -> 'YYYY-MM-DDTHH:MM'
  if(!s) return ''; const m=s.match(/(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})/); return m? m[1]+'T'+m[2] : '';
}
function deInputDateTime(s){ // 'YYYY-MM-DDTHH:MM' -> 'YYYY-MM-DD HH:MM:SS'
  if(!s) return ''; return s.replace('T',' ')+':00';
}
function parseCoords(txt){
  if(!txt) return [];
  return txt.trim().split(/\s+/).map(tok=>{
    const p=tok.split(','); return [parseFloat(p[1]), parseFloat(p[0])]; // [lat,lng]
  }).filter(c=>!isNaN(c[0])&&!isNaN(c[1]));
}
/* Helpers XML/DOM tolerantes a namespaces */
function getByLocal(node,local){
  const all = node.getElementsByTagName('*'); const out=[];
  for(const el of all){ if(el.localName===local) out.push(el); }
  return out;
}
function textLocal(node,local){
  const els=getByLocal(node,local);
  return els.length? (els[0].textContent||'').trim() : '';
}
function esc(s){ return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function val(id){ return document.getElementById(id).value; }
function set(id,v){ document.getElementById(id).value = v==null?'':v; }
function descargar(txt,nombre,tipo){ const b=new Blob([txt],{type:tipo}); const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download=nombre; a.click(); }

init();
</script>
</body>
</html>
```

### A.2 — Plataforma_PMTs.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestión PMT Institucional</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/buttons/2.3.6/css/buttons.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet">

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .epm-header { background-color: white; border-bottom: 4px solid #009300; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 8px 20px; }
        .epm-title { color: #009300; font-weight: bold; font-size: 19px; margin-left: 15px; vertical-align: middle; line-height: 1.15; }
        .epm-card-header { background-color: #009300; color: white; font-weight: bold; padding: 8px 15px; font-size: 0.95rem; }
        .epm-btn { background-color: #b7c200; color: #000; font-weight: bold; border: none; transition: 0.3s; }
        .epm-btn:hover { background-color: #99a800; transform: translateY(-1px); }
        .epm-btn-play { background-color: #009300; color: white; font-weight: bold; }

        .map-wrapper { height: 100%; min-height: 72vh; border: 3px solid #009300; border-radius: 8px; margin-bottom: 0; overflow: hidden; position: relative; background: #e9ecef; }
        .table-wrapper { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 4px solid #b7c200; }
        .table-dark { background-color: #008c6b !important; }
        .temporal-box { background-color: #e9f5e9; border: 2px solid #009300; border-radius: 8px; padding: 10px 15px; margin-bottom: 15px; }
        .fecha-activa-display { font-size: 1.2rem; color: #d56b00; font-weight: bold; background: white; padding: 3px 15px; border-radius: 5px; border: 1px solid #d56b00; }

        .select2-container--bootstrap-5 .select2-selection {
            font-size: 0.8rem; min-height: 31px; max-height: 110px; overflow-y: auto; overflow-x: hidden;
        }
        .select2-container--bootstrap-5 .select2-selection--multiple .select2-selection__rendered {
            padding: 2px 4px; display: flex; flex-wrap: wrap; gap: 2px; max-width: 100%;
        }
        .select2-container--bootstrap-5 .select2-selection--multiple .select2-selection__choice {
            background-color: #009300; border-color: #007a00; color: white; font-size: 0.7rem;
            padding: 0 6px; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 1;
        }
        .select2-container--bootstrap-5 .select2-selection--multiple .select2-selection__choice__remove { color: rgba(255,255,255,0.8); }
        .select2-container--bootstrap-5 .select2-selection--multiple .select2-selection__choice__remove:hover { color: white; }
        .select2-container { width: 100% !important; max-width: 100% !important; }
        .select2-dropdown { min-width: 100%; max-width: 300px; font-size: 0.8rem; z-index: 9999; }
        .select2-results__option { padding: 4px 8px; white-space: normal; word-break: break-word; }

        /* =================== DISEÑO MODAL PDF =================== */
        .pdf-modal-backdrop {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 2000; overflow-y: auto;
            display: none; justify-content: center; padding: 30px 0;
        }
        .pdf-controls { position: fixed; top: 20px; right: 30px; z-index: 2010; }
        .a4-preview { width: 210mm; min-height: 297mm; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.3); padding-bottom: 20mm; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; }
        .pdf-header-banner { background-color: #009300; color: white; padding: 20px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 5px solid #b7c200; }
        .pdf-header-title { margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }
        .pdf-header-date { font-size: 12px; opacity: 0.9; }
        .pdf-body { padding: 25px 30px; }
        .pdf-grid { margin-bottom: 20px; }
        
        /* Modificación para expandir los KPIs horizontalmente */
        .pdf-kpi-container { width: 100%; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .pdf-kpi-box { background: #f8f9fa; border-left: 4px solid #009300; padding: 12px 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .pdf-kpi-title { font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 4px; font-weight: bold; }
        .pdf-kpi-value { font-size: 18px; font-weight: bold; color: #343a40; margin: 0; }
        
        .pdf-section-title { font-size: 14px; font-weight: bold; color: #009300; text-transform: uppercase; margin: 20px 0 10px 0; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; }
        .pdf-table { width: 100%; border-collapse: collapse; }
        .pdf-table th, .pdf-table td { border: 1px solid #dee2e6; padding: 6px 7px; font-size: 9px; vertical-align: top; }
        .pdf-table th { background-color: #f1f3f5; color: #495057; }
        .pdf-table tr { page-break-inside: avoid; }
        .pdf-progress-wrap { margin-bottom: 10px; page-break-inside: avoid; }
        .pdf-progress-header { display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 3px; font-weight: bold; }
        .pdf-progress-bar { background: #e9ecef; border-radius: 3px; height: 8px; width: 100%; }
        .pdf-progress-fill { height: 100%; border-radius: 3px; }

        /* Tarjetas críticas: estilo limpio con acento naranja de marca EPM (#d56b00) */
        .critico-card {
            border: 1px solid #eadfd6; border-left: 4px solid #d56b00; border-radius: 6px;
            background: #ffffff; padding: 12px 15px;
            margin-bottom: 10px; page-break-inside: avoid;
        }
        .critico-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; border-bottom: 1px solid #f0eae4; padding-bottom: 6px; }
        .critico-card-badge { background: #d56b00; color: white; font-size: 9px; font-weight: bold; padding: 2px 9px; border-radius: 10px; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap; }
        .critico-card-title { font-size: 11px; font-weight: bold; color: #995000; }
        .critico-card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 15px; }
        .critico-field-label { font-size: 8px; color: #a35400; font-weight: bold; text-transform: uppercase; letter-spacing: 0.2px; margin-bottom: 2px; }
        .critico-field-value { font-size: 9px; color: #333333; font-weight: 500; line-height: 1.4; }
        .critico-fechas-bar { margin-top: 8px; background: #fbf3ec; border: 1px solid #eadfd6; border-radius: 4px; padding: 5px 10px; font-size: 9px; color: #995000; font-weight: bold; }
        .critico-agrupada-nota { font-size: 8px; color: #a35400; font-style: italic; margin-top: 2px; }
        .critico-nota-real { font-size: 8px; color: #6c757d; font-style: italic; font-weight: normal; margin-top: 3px; }

        .semaforo-verde   { color: #009300; font-weight: bold; }
        .semaforo-amarillo { color: #e6a800; font-weight: bold; }
        .semaforo-rojo    { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>

<div class="epm-header mb-3 d-flex justify-content-between align-items-center">
    <div>
        <img src="logo_epm.jpg" onerror="this.src='logo_epm.png'" alt="Logo EPM" style="height: 45px;">
        <span class="epm-title">PLATAFORMA DE CONTROL Y ARTICULACIÓN DE PMTs</span>
    </div>
    
    <div class="d-flex gap-2">
        <a href="Generador_KMZ.html" target="_blank" class="btn epm-btn-play shadow-sm">🛠️ Generar KMZ</a>
        <button onclick="openPdfPreview()" class="btn epm-btn shadow-sm">
            <span id="btn-pdf-text">📄 Generar Informe PDF Ejecutivo</span>
        </button>
    </div>
</div>

<div class="container-fluid px-3 mt-3">
    <div id="error-alerta" class="alert alert-danger d-none fw-bold" role="alert">
        ⚠️ ATENCIÓN: El navegador bloqueó los datos (CORS). Sube esta carpeta a GitHub y ábrela desde el enlace web.
    </div>

    <!-- ZONA MEDIA: dos columnas. Izquierda = controles (1/3). Derecha = mapa vertical (2/3). -->
    <div class="row g-3 mb-3 align-items-stretch">

        <!-- COLUMNA IZQUIERDA: recorrido temporal + filtros, apilados -->
        <div class="col-12 col-lg-4 d-flex flex-column">

            <div class="temporal-box mb-3">
                <div class="row g-2 align-items-end">
                    <div class="col-6">
                        <label class="form-label fw-bold text-success mb-1">⏱️ Inicio Recorrido:</label>
                        <input type="date" id="repInicio" class="form-control form-control-sm">
                    </div>
                    <div class="col-6">
                        <label class="form-label fw-bold text-success mb-1">Fin Recorrido:</label>
                        <input type="date" id="repFin" class="form-control form-control-sm">
                    </div>
                    <div class="col-6">
                        <label class="form-label fw-bold mb-1">Avanzar cada:</label>
                        <select id="velocidadPaso" class="form-select form-select-sm">
                            <option value="1">1 Día</option>
                            <option value="7">1 Semana</option>
                            <option value="30">1 Mes</option>
                        </select>
                    </div>
                    <div class="col-6">
                        <label class="form-label fw-bold mb-1">Velocidad:</label>
                        <select id="velocidadReproduccion" class="form-select form-select-sm">
                            <option value="2400">0.5X (Lento)</option>
                            <option value="1200" selected>1X (Normal)</option>
                            <option value="600">2X (Rápido)</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <button id="btnPlay" class="btn btn-sm epm-btn-play w-100">▶ Iniciar Recorrido</button>
                    </div>
                    <div class="col-12 text-center d-flex align-items-center justify-content-center gap-2 mt-1">
                        <span class="fw-bold text-secondary" style="font-size: 0.85rem;">En Mapa:</span>
                        <div id="fechaActualVisual" class="fecha-activa-display">---</div>
                    </div>
                </div>
            </div>

            <div class="card flex-grow-1" style="border-color: #009300;">
                <div class="card-header epm-card-header">⚙️ Panel de Filtros Específicos</div>
                <div class="card-body py-2">
                    <div class="row g-2 align-items-end">
                        <div class="col-6" style="overflow:hidden; min-width:0;">
                            <label class="fw-bold text-success form-label mb-1">Contratista:</label>
                            <select id="filtroContratista" class="form-select form-select-sm" multiple></select>
                        </div>
                        <div class="col-6" style="overflow:hidden; min-width:0;">
                            <label class="fw-bold text-success form-label mb-1">Contrato:</label>
                            <select id="filtroContrato" class="form-select form-select-sm" multiple></select>
                        </div>
                        <div class="col-6" style="overflow:hidden; min-width:0;">
                            <label class="fw-bold text-success form-label mb-1">Frente:</label>
                            <select id="filtroFrente" class="form-select form-select-sm" multiple></select>
                        </div>
                        <div class="col-6" style="overflow:hidden; min-width:0;">
                            <label class="fw-bold text-success form-label mb-1">Interferencia/Estado:</label>
                            <select id="filtroInterferencia" class="form-select form-select-sm" multiple></select>
                        </div>
                        <div class="col-12" style="overflow:hidden; min-width:0;">
                            <label class="fw-bold text-success form-label mb-1">🏛️ Municipio:</label>
                            <select id="filtroMunicipio" class="form-select form-select-sm" multiple></select>
                        </div>
                        <div class="col-6">
                            <label class="fw-bold text-secondary form-label mb-1">F. Inicio:</label>
                            <input type="date" id="filtroInicio" class="form-control form-control-sm">
                        </div>
                        <div class="col-6">
                            <label class="fw-bold text-secondary form-label mb-1">F. Fin:</label>
                            <input type="date" id="filtroFin" class="form-control form-control-sm">
                        </div>
                        <div class="col-12">
                            <button id="btnLimpiar" class="btn epm-btn btn-sm w-100">🧹 Limpiar Filtros</button>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- COLUMNA DERECHA: mapa vertical -->
        <div class="col-12 col-lg-8">
            <div class="map-wrapper h-100">
                <iframe id="mapaIframe" src="about:blank" width="100%" height="100%" style="border:none;"></iframe>
            </div>
        </div>

    </div>

    <div class="table-wrapper">
        <div class="table-responsive">
            <table id="tablaDatos" class="table table-sm table-striped table-hover align-middle" style="width:100%; font-size: 0.9rem;">
                <thead class="table-dark text-white">
                    <tr>
                        <th>Categoría</th>
                        <th>Contrato</th>
                        <th>Contratista</th>
                        <th>Municipio</th>
                        <th>Frente</th>
                        <th>Dirección</th>
                        <th>Estado/Cierre</th>
                        <th>Horario</th>
                        <th>Inicio</th>
                        <th>Fin</th>
                        <th>Días</th>
                    </tr>
                </thead>
                <tbody id="cuerpoTabla"></tbody>
            </table>
        </div>
    </div>
</div>

<div id="pdfModal" class="pdf-modal-backdrop">
    <div class="pdf-controls d-flex gap-2 align-items-center">
        <div class="form-check form-switch bg-white px-3 py-2 rounded shadow d-flex align-items-center gap-2" style="margin:0;">
            <input class="form-check-input" type="checkbox" id="chkAgruparCriticas" checked style="cursor:pointer;">
            <label class="form-check-label fw-bold" for="chkAgruparCriticas" style="font-size:0.8rem; cursor:pointer;">
                Agrupar críticas (mismo Contratista + Contrato + Período)
            </label>
        </div>
        <input type="file" id="inputMapaImg" accept="image/*" style="display:none;" onchange="cargarImagenMapa(event)">
        <button id="btnAdjuntarMapa" onclick="document.getElementById('inputMapaImg').click()" class="btn btn-light fw-bold shadow">📎 Adjuntar imagen del mapa</button>
        <button onclick="closePdfPreview()" class="btn btn-secondary fw-bold shadow">✖ Cancelar</button>
        <button id="btnConfirmPdf" onclick="downloadPDF()" class="btn epm-btn fw-bold shadow">📥 Confirmar Descarga PDF</button>
    </div>

    <div id="pdf-content" class="a4-preview">
        <div class="pdf-header-banner">
            <div>
                <h1 class="pdf-header-title">INFORME TÉCNICO DE GESTIÓN PMT</h1>
                <div style="font-size:12px; font-weight:bold; letter-spacing:0.3px; opacity:0.95; margin-top:2px;">ÁREA CENTRO DE GESTIÓN SERVICIOS TÉCNICOS</div>
                <div class="pdf-header-date" id="pdf-date-gen"></div>
            </div>
            <div style="background:white; padding:5px; border-radius:4px;">
                <img src="logo_epm.jpg" onerror="this.src='logo_epm.png'" style="height: 35px;" alt="EPM">
            </div>
        </div>

        <div class="pdf-body">
            <div class="pdf-grid">
                <div class="pdf-kpi-container">
                    <div class="pdf-kpi-box">
                        <div class="pdf-kpi-title">Registros Activos</div>
                        <p class="pdf-kpi-value" id="pdf-total-reg">0</p>
                    </div>
                    <div class="pdf-kpi-box" style="border-left-color:#d56b00;">
                        <div class="pdf-kpi-title">Interferencias Críticas</div>
                        <p class="pdf-kpi-value" id="pdf-total-crit" style="color:#d56b00;">0</p>
                    </div>
                    <div class="pdf-kpi-box" style="border-left-color:#0d6efd;">
                        <div class="pdf-kpi-title">Contratos Involucrados</div>
                        <p class="pdf-kpi-value" id="pdf-total-cont">0</p>
                    </div>
                    <div class="pdf-kpi-box" style="border-left-color:#6c757d;">
                        <div class="pdf-kpi-title">Rango de Fechas</div>
                        <p class="pdf-kpi-value" id="pdf-date-range" style="font-size:14px;">N/A</p>
                    </div>
                </div>
            </div>

            <div id="pdf-executive-summary" style="font-size:11px; text-align:justify; margin-bottom:20px; line-height:1.5; background:#f8f9fa; padding:10px; border-radius:4px; border:1px solid #e9ecef;"></div>

            <div id="pdf-mapa-section" style="display:none; margin-bottom:20px; page-break-inside:avoid;">
                <div class="pdf-section-title">🗺️ Vista del Mapa (según filtros aplicados)</div>
                <div style="text-align:center;">
                    <img id="pdf-mapa-img" src="" alt="Mapa" style="max-width:100%; max-height:120mm; border:1px solid #dee2e6; border-radius:4px;">
                </div>
            </div>

            <div id="pdf-criticos-section" style="display:none;">
                <div class="pdf-section-title" style="color:#d56b00; border-bottom-color:#e8c9a8;">⚠️ Detalle de Interferencias Críticas</div>
                <div id="pdf-criticos-container" style="margin-bottom:20px;"></div>
            </div>

            <div class="pdf-section-title">📊 Estado de Avance en Tiempo</div>
            <div id="pdf-progress-container" style="margin-bottom:20px; column-count:2; column-gap:20px;"></div>

            <div class="pdf-section-title">
                📋 Detalle Completo de Registros
                <span style="font-size:9px; color:#6c757d; font-weight:normal;">(solo trazados normales; las interferencias se detallan en su sección)</span>
            </div>
            <table class="table pdf-table">
                <thead>
                    <tr>
                        <th style="width:10%">Categoría</th>
                        <th style="width:11%">Contrato</th>
                        <th style="width:12%">Contratista</th>
                        <th style="width:12%">Frente</th>
                        <th style="width:10%">Estado/Cierre</th>
                        <th style="width:10%">Horario</th>
                        <th style="width:13%">Fechas</th>
                        <th style="width:11%">Vigencia 🚦</th>
                    </tr>
                </thead>
                <tbody id="pdf-table-body"></tbody>
            </table>

            <div style="text-align:center; font-size:9px; color:#868e96; margin-top:30px; border-top:1px solid #dee2e6; padding-top:10px;">
                Documento generado automáticamente por el Visor Inteligente de Gestión PMT – Grupo EPM. Documento de uso técnico.
            </div>
        </div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.3.6/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.bootstrap5.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.3.6/js/buttons.html5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

<script>
/* =========================================================================
   VARIABLES GLOBALES
   ========================================================================= */
var mapaCargado         = false;
var reproduccionActiva  = false;
var reproduccionPausada = false;
var fechaReproduccion   = null;
var reproductorInterval = null;
var imagenMapaPDF       = null;   // imagen del mapa adjuntada manualmente para el informe

/* Recibe la imagen que el usuario adjunta (recorte del mapa) y la guarda para el PDF */
function cargarImagenMapa(evento) {
    var archivo = evento.target.files && evento.target.files[0];
    if (!archivo) return;
    var lector = new FileReader();
    lector.onload = function(e) {
        imagenMapaPDF = e.target.result;             // imagen en formato base64
        var btn = document.getElementById('btnAdjuntarMapa');
        if (btn) { btn.innerHTML = '✅ Imagen adjunta (cambiar)'; btn.classList.remove('btn-light'); btn.classList.add('epm-btn'); }
        aplicarImagenMapaEnInforme();                // la muestra en la vista previa
    };
    lector.readAsDataURL(archivo);
}

/* Muestra u oculta la sección de la imagen del mapa dentro del informe */
function aplicarImagenMapaEnInforme() {
    var sec = document.getElementById('pdf-mapa-section');
    var img = document.getElementById('pdf-mapa-img');
    if (!sec || !img) return;
    if (imagenMapaPDF) { img.src = imagenMapaPDF; sec.style.display = 'block'; }
    else { img.src = ''; sec.style.display = 'none'; }
}

/* =====================================================
   parseCSVRow (BLOQUE INTACTO ANTI-CORS)
   ===================================================== */
function parseCSVRow(str) {
    let arr = [], quote = false, start = 0;
    for (let i = 0; i < str.length; i++) {
        if (str[i] === '"') quote = !quote;
        if (str[i] === ',' && !quote) {
            arr.push(str.substring(start, i).replace(/^"|"$/g, '').trim());
            start = i + 1;
        }
    }
    arr.push(str.substring(start).replace(/^"|"$/g, '').trim());
    return arr;
}

function cleanDate(dateStr) {
    if (!dateStr || dateStr === 'N/A') return null;
    let p = dateStr.split('-');
    return new Date(p[0], p[1] - 1, p[2]);
}

/* =========================================================================
   SEMÁFORO DE VIGENCIA — días hábiles L-V
   ========================================================================= */
function calcularSemaforo(fechaFinStr) {
    var hoy = new Date(); hoy.setHours(0,0,0,0);
    var fin = cleanDate(fechaFinStr);
    if (!fin) return { diasHabiles: null, color: '#6c757d', label: 'Sin fecha', emoji: '⚫' };
    fin.setHours(0,0,0,0);
    if (fin < hoy) return { diasHabiles: 0, color: '#dc3545', label: 'Vencido', emoji: '🔴' };
    var cuenta = 0, cursor = new Date(hoy);
    cursor.setDate(cursor.getDate() + 1);
    while (cursor <= fin) {
        var d = cursor.getDay();
        if (d !== 0 && d !== 6) cuenta++;
        cursor.setDate(cursor.getDate() + 1);
    }
    if (cuenta > 20)  return { diasHabiles: cuenta, color: '#009300', label: cuenta + ' días hábiles', emoji: '🟢' };
    if (cuenta >= 15) return { diasHabiles: cuenta, color: '#e6a800', label: cuenta + ' días hábiles', emoji: '🟡' };
    return { diasHabiles: cuenta, color: '#dc3545', label: cuenta + ' días hábiles', emoji: '🔴' };
}

/* =========================================================================
   syncMap — mantiene el mapa vivo en el dashboard
   ========================================================================= */
function syncMap() {
    if (!mapaCargado || !window.$.fn.dataTable || !$.fn.dataTable.isDataTable('#tablaDatos')) return;
    var table = $('#tablaDatos').DataTable();
    var frentesActivos = [];
    table.rows({ filter: 'applied' }).data().each(function(row) { frentesActivos.push(row[4]); });

    var iframeWin = document.getElementById('mapaIframe').contentWindow;
    if (iframeWin.map) {
        iframeWin.map.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties) {
                var props = layer.feature.properties, nombreMapa = '';
                for (let k in props) {
                    if (['frente','frentes','name'].includes(k.toLowerCase())) { nombreMapa = String(props[k]); break; }
                }
                let vis = nombreMapa
                    ? frentesActivos.some(f => f.includes(nombreMapa) || nombreMapa.includes(f))
                    : false;
                if (layer.getElement) {
                    let el = layer.getElement();
                    if (el) el.style.display = vis ? '' : 'none';
                }
            }
        });
    }
}

/* =========================================================================
   REPRODUCTOR — funciones globales
   ========================================================================= */
function iniciarReproductor(table) {
    var s = $('#repInicio').val(), e = $('#repFin').val();
    if (!s || !e) { alert('⚠️ Selecciona Fecha de Inicio y Fin del recorrido.'); return; }
    reproduccionActiva = true; reproduccionPausada = false;
    fechaReproduccion = cleanDate(s);
    $('#btnPlay').text('⏸ Pausar').removeClass('epm-btn-play').addClass('btn-danger');
    iniciarCiclo(table);
}
function reanudarReproductor(table) {
    reproduccionActiva = true; reproduccionPausada = false;
    $('#btnPlay').text('⏸ Pausar').removeClass('epm-btn-play btn-warning').addClass('btn-danger');
    iniciarCiclo(table);
}
function pausarReproductor() {
    reproduccionActiva = false; reproduccionPausada = true;
    clearInterval(reproductorInterval);
    $('#btnPlay').text('▶ Reanudar').removeClass('btn-danger').addClass('btn-warning');
    if (fechaReproduccion) {
        var vd = fechaReproduccion.getFullYear() + '-' + String(fechaReproduccion.getMonth()+1).padStart(2,'0') + '-' + String(fechaReproduccion.getDate()).padStart(2,'0');
        $('#fechaActualVisual').text('⏸ ' + vd);
    }
}
function detenerReproductor(resetTotal) {
    reproduccionActiva = false; reproduccionPausada = false;
    clearInterval(reproductorInterval);
    if (resetTotal) fechaReproduccion = null;
    $('#btnPlay').text('▶ Iniciar Recorrido').removeClass('btn-danger btn-warning').addClass('epm-btn-play');
    if (!$('#fechaActualVisual').text().includes('Fin')) $('#fechaActualVisual').text('---');
}
function iniciarCiclo(table) {
    var fin  = cleanDate($('#repFin').val());
    var paso = parseInt($('#velocidadPaso').val());
    var ms   = parseInt($('#velocidadReproduccion').val());
    reproductorInterval = setInterval(function() {
        if (fechaReproduccion > fin) { detenerReproductor(false); $('#fechaActualVisual').text('✅ Fin'); return; }
        var vd = fechaReproduccion.getFullYear() + '-' + String(fechaReproduccion.getMonth()+1).padStart(2,'0') + '-' + String(fechaReproduccion.getDate()).padStart(2,'0');
        $('#fechaActualVisual').text(vd);
        table.draw();
        fechaReproduccion.setDate(fechaReproduccion.getDate() + paso);
    }, ms);
}

/* =========================================================================
   DOCUMENT READY — punto de entrada único
   ========================================================================= */
$(document).ready(function() {
    function esperarDataTables(cb, intentos) {
        intentos = intentos || 0;
        if (window.$.fn && window.$.fn.dataTable && window.$.fn.dataTable.ext) {
            cb();
        } else if (intentos < 100) {
            setTimeout(function(){ esperarDataTables(cb, intentos + 1); }, 100);
        } else {
            console.error('[PMT] DataTables no cargó después de 10s.');
        }
    }

    esperarDataTables(function() {
        $('#mapaIframe').on('load', function() {
            mapaCargado = true;
            if ($.fn.dataTable.isDataTable('#tablaDatos')) syncMap();
        });

        /* =========================================================
           SELECTOR INTELIGENTE DEL MAPA
           Carga el mapa sin importar cómo lo hayas subido:
             1) Si 'index.html' está al lado de la Plataforma -> lo usa.
             2) Si arrastraste la carpeta completa de qgis2web
                (nombre con fecha, que cambia cada vez), le pregunta
                a GitHub cuál es la MÁS RECIENTE y usa su index.html.
             3) Si aún existe el antiguo 'mapa_qgis.html' -> lo usa.
           ========================================================= */
        (function seleccionarMapa() {
            var iframe = document.getElementById('mapaIframe');
            function cargar(url) { iframe.src = url; }

            // Verifica si un archivo existe (sin descargarlo completo)
            function existe(url) {
                return fetch(url + '?nocache=' + new Date().getTime(), { method: 'HEAD' })
                    .then(function(r) { return r.ok ? url : null; })
                    .catch(function() { return null; });
            }

            // Pregunta a GitHub por la carpeta qgis2web_* más reciente
            function buscarCarpetaGitHub() {
                try {
                    var host = window.location.hostname;             // ej: ljmarinza.github.io
                    if (host.indexOf('github.io') === -1) return Promise.resolve(null);
                    var owner = host.split('.')[0];                  // ej: ljmarinza
                    var repo  = window.location.pathname.split('/').filter(Boolean)[0]; // ej: Interferencias_PMT
                    if (!owner || !repo) return Promise.resolve(null);
                    var api = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/';
                    return fetch(api)
                        .then(function(r) { return r.ok ? r.json() : null; })
                        .then(function(lista) {
                            if (!Array.isArray(lista)) return null;
                            var carpetas = lista.filter(function(x) {
                                return x.type === 'dir' && /^qgis2web/i.test(x.name);
                            });
                            if (!carpetas.length) return null;
                            // Ordena de más reciente a más antigua (el nombre lleva la fecha)
                            carpetas.sort(function(a, b) { return a.name < b.name ? 1 : -1; });
                            return carpetas[0].name + '/index.html';
                        })
                        .catch(function() { return null; });
                } catch (e) { return Promise.resolve(null); }
            }

            // Orden de intentos: index.html suelto -> carpeta qgis2web -> mapa_qgis.html
            existe('index.html').then(function(u1) {
                if (u1) return cargar(u1);
                return buscarCarpetaGitHub().then(function(u2) {
                    if (u2) return cargar(u2);
                    return existe('mapa_qgis.html').then(function(u3) {
                        if (u3) cargar(u3);
                        else console.error('[PMT] No se encontró el mapa (ni index.html, ni carpeta qgis2web, ni mapa_qgis.html).');
                    });
                });
            });
        })();

        $.fn.dataTable.ext.search.push(function(settings, data) {
            var pC  = ($('#filtroContratista').val()  || []).filter(function(v){ return v && v !== ''; });
            var pCt = ($('#filtroContrato').val()      || []).filter(function(v){ return v && v !== ''; });
            var pF  = ($('#filtroFrente').val()        || []).filter(function(v){ return v && v !== ''; });
            var pI  = ($('#filtroInterferencia').val() || []).filter(function(v){ return v && v !== ''; });
            var pM  = ($('#filtroMunicipio').val()     || []).filter(function(v){ return v && v !== ''; });

            if (pC.length  && !pC.some(function(v){  return data[2] && data[2].includes(v); })) return false;
            if (pCt.length && !pCt.some(function(v){ return data[1] && data[1].includes(v); })) return false;
            if (pF.length  && !pF.some(function(v){  return data[4] && data[4].includes(v); })) return false;
            if (pI.length  && !pI.some(function(v){  return data[6] === v || data[0] === v; })) return false;
            if (pM.length  && !pM.some(function(v){  return data[3] && data[3].includes(v); })) return false;

            var rowStart = cleanDate(data[8]), rowEnd = cleanDate(data[9]);
            if (reproduccionActiva && fechaReproduccion) {
                if (rowStart && rowEnd && fechaReproduccion >= rowStart && fechaReproduccion <= rowEnd) return true;
                return false;
            }
            /* FILTRO DE FECHAS POR CRUCE DE PERÍODO
               Una fila pasa si su período (inicio→fin) se cruza con la ventana
               que elige el usuario, aunque haya empezado antes o termine después.
               Es decir: sigue activa en algún momento dentro del rango.
               Regla de cruce: inicioFila <= finVentana  Y  finFila >= inicioVentana.
               Filas sin fechas válidas quedan ocultas mientras haya filtro. */
            var fInicio = cleanDate($('#filtroInicio').val()), fFin = cleanDate($('#filtroFin').val());
            if (fInicio || fFin) {
                if (!rowStart || !rowEnd) return false;
                if (fFin && rowStart > fFin) return false;      // empieza después de la ventana
                if (fInicio && rowEnd < fInicio) return false;  // termina antes de la ventana
            }
            return true;
        });

        var s2Cfg = {
            theme: 'bootstrap-5', placeholder: 'Todos', allowClear: true,
            closeOnSelect: false, dropdownParent: $('body'),
            language: { noResults: function(){ return 'Sin resultados'; } }
        };
        $('#filtroContratista, #filtroContrato, #filtroFrente, #filtroInterferencia, #filtroMunicipio').select2(s2Cfg);

        /* LECTURA CSV - INTACTA */
        fetch('reporte_dinamico.csv?nocache=' + new Date().getTime())
        .then(function(r) { if (!r.ok) throw new Error('CORS'); return r.text(); })
        .then(function(data) {
            var filas = data.split('\n').slice(1);
            var html = '';
            filas.forEach(function(fila) {
                if (fila.trim() === '') return;
                var cols = parseCSVRow(fila);
                if (cols.length >= 8) {
                    while (cols.length < 11) cols.push('N/A');
                    html += '<tr>' + cols.map(function(c){ return '<td>' + (c || 'N/A') + '</td>'; }).join('') + '</tr>';
                }
            });
            $('#cuerpoTabla').html(html);

            var table = $('#tablaDatos').DataTable({
                language: { url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json' },
                pageLength: 5, lengthMenu: [5, 10, 25, 50, 'Todos'],
                order: [[0, 'desc']], columnDefs: [{ targets: 3, visible: true }],
                dom: "<'row'<'col-sm-12 col-md-4'l><'col-sm-12 col-md-8 text-end'B>>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
                buttons: [{ extend: 'excelHtml5', text: '📥 Exportar a Excel/CSV', className: 'btn btn-sm btn-success fw-bold' }]
            });

            /* =====================================================================
               FACETA CRUZADA JERÁRQUICA (Puntos 1, 2, 3 y 4)
               ---------------------------------------------------------------------
               Cada lista se llena recorriendo TODOS los registros del CSV (no solo
               los ya filtrados) y aplicando únicamente los filtros de las OTRAS
               listas, nunca el suyo propio. Resultado:
                 - Una lista jamás se limita a sí misma: puedes marcar varios
                   elementos aunque no tengan relación entre ellos (Puntos 1-3)
                   y sin tener que salir y volver a entrar (Punto 4).
                 - Se mantiene la jerarquía en ambos sentidos: si eliges
                   Contratistas, Contrato y Frente se acotan a ellos; si eliges
                   primero Contratos, Contratista y Frente se acotan a esos.
                 - Las fechas NO intervienen aquí: son independientes.
               ===================================================================== */

            // Divide un valor de celda en sus partes ("A vs B" o "A / B")
            function partes(valor, separador) {
                if (!valor || valor === 'N/A') return [];
                return valor.split(separador).map(function(s){ return s.trim(); }).filter(Boolean);
            }

            // ¿La fila coincide con una selección? (vacío = sin filtro = pasa)
            function coincide(seleccion, valoresFila) {
                if (!seleccion || !seleccion.length) return true;
                return seleccion.some(function(sel){ return valoresFila.indexOf(sel) !== -1; });
            }

            // El parámetro 'origen' es el id de la lista que el usuario acaba de
            // cambiar. Esa lista NO se reconstruye (se deja intacta para que pueda
            // seguir marcando opciones sin que se le trabe). Solo se refrescan las otras.
            function updateDropdowns(origen) {
                var selC  = ($('#filtroContratista').val()  || []).filter(Boolean);
                var selCt = ($('#filtroContrato').val()     || []).filter(Boolean);
                var selF  = ($('#filtroFrente').val()       || []).filter(Boolean);
                var selI  = ($('#filtroInterferencia').val() || []).filter(Boolean);
                var selM  = ($('#filtroMunicipio').val()     || []).filter(Boolean);

                var sC = new Set(), sCt = new Set(), sF = new Set(), sI = new Set(), sM = new Set();

                table.rows().data().each(function(row) {
                    var vC  = partes(row[2], ' vs ');   // contratistas de la fila
                    var vCt = partes(row[1], ' vs ');   // contratos de la fila
                    var vF  = partes(row[4], ' / ');    // frentes de la fila
                    var vI  = (row[6] && row[6] !== 'N/A') ? [row[6].trim()] : [];
                    var vIcat = (row[0] && row[0] !== 'N/A') ? [row[0].trim()] : [];
                    // Municipio: valor real (para coincidir) y valor "opción" (excluye "Varios"/"N/A" del menú)
                    var vMun    = (row[3] && row[3] !== 'N/A') ? [row[3].trim()] : [];
                    var vMunOpt = (row[3] && row[3] !== 'N/A' && row[3] !== 'Varios') ? [row[3].trim()] : [];

                    // Para Interferencia/Estado la coincidencia mira tanto la columna
                    // Estado/Cierre (row[6]) como la Categoría (row[0]), igual que el filtro real.
                    var matchI = !selI.length || selI.some(function(sel){
                        return vI.indexOf(sel) !== -1 || vIcat.indexOf(sel) !== -1;
                    });
                    var matchM = coincide(selM, vMun);   // ¿la fila pertenece al municipio elegido?

                    // CONTRATISTA: respeta Contrato + Frente + Interferencia + Municipio (no a sí mismo)
                    if (coincide(selCt, vCt) && coincide(selF, vF) && matchI && matchM) {
                        vC.forEach(function(v){ sC.add(v); });
                    }
                    // CONTRATO: respeta Contratista + Frente + Interferencia + Municipio
                    if (coincide(selC, vC) && coincide(selF, vF) && matchI && matchM) {
                        vCt.forEach(function(v){ sCt.add(v); });
                    }
                    // FRENTE: respeta Contratista + Contrato + Interferencia + Municipio
                    if (coincide(selC, vC) && coincide(selCt, vCt) && matchI && matchM) {
                        vF.forEach(function(v){ sF.add(v); });
                    }
                    // INTERFERENCIA/ESTADO: respeta Contratista + Contrato + Frente + Municipio
                    if (coincide(selC, vC) && coincide(selCt, vCt) && coincide(selF, vF) && matchM) {
                        vI.forEach(function(v){ sI.add(v); });
                    }
                    // MUNICIPIO: respeta Contratista + Contrato + Frente + Interferencia
                    if (coincide(selC, vC) && coincide(selCt, vCt) && coincide(selF, vF) && matchI) {
                        vMunOpt.forEach(function(v){ sM.add(v); });
                    }
                });

                // Nos aseguramos de conservar lo ya seleccionado aunque el conjunto
                // recalculado no lo incluyera (evita que se "pierda" una selección).
                selC.forEach(function(v){ sC.add(v); });
                selCt.forEach(function(v){ sCt.add(v); });
                selF.forEach(function(v){ sF.add(v); });
                selI.forEach(function(v){ sI.add(v); });
                selM.forEach(function(v){ sM.add(v); });

                function pop(id, set, prev) {
                    // No tocar la lista que el usuario está usando en este momento
                    if (origen && ('#' + origen) === id) return;
                    var $s = $(id); $s.empty();
                    Array.from(set).sort().forEach(function(val){
                        var isSel = prev.indexOf(val) !== -1;
                        $s.append(new Option(val, val, isSel, isSel));
                    });
                    $s.trigger('change.select2');
                }
                pop('#filtroContratista',   sC,  selC);
                pop('#filtroContrato',      sCt, selCt);
                pop('#filtroFrente',        sF,  selF);
                pop('#filtroInterferencia', sI,  selI);
                pop('#filtroMunicipio',     sM,  selM);
            }

            updateDropdowns();

            $('#filtroContratista, #filtroContrato, #filtroFrente, #filtroInterferencia, #filtroMunicipio, #filtroInicio, #filtroFin')
                .on('change', function() {
                    table.draw();
                    updateDropdowns(this.id);   // pasa la lista que cambió para no reconstruirla
                });

            $('#btnLimpiar').click(function() {
                $('#filtroContratista, #filtroContrato, #filtroFrente, #filtroInterferencia, #filtroMunicipio').val(null).trigger('change');
                $('#filtroInicio, #filtroFin, #repInicio, #repFin').val('');
                detenerReproductor(true);
                table.draw(); updateDropdowns();
            });

            table.on('draw.dt', syncMap);

            $('#btnPlay').click(function() {
                if (reproduccionActiva)       pausarReproductor();
                else if (reproduccionPausada) reanudarReproductor(table);
                else                          iniciarReproductor(table);
            });

            $('#velocidadReproduccion').on('change', function() {
                if (reproduccionActiva) { clearInterval(reproductorInterval); iniciarCiclo(table); }
            });

            if (mapaCargado) syncMap();
        })
        .catch(function() { document.getElementById('error-alerta').classList.remove('d-none'); });
    });
});


/* =========================================================================
   GENERADOR DE PDF Y MODAL (SIN MAPA)
   ========================================================================= */
function openPdfPreview() {
    if (!window.$ || !$.fn.dataTable || !$.fn.dataTable.isDataTable('#tablaDatos')) {
        alert('La tabla aún está cargando. Espera unos segundos e intenta de nuevo.');
        return;
    }

    var table = $('#tablaDatos').DataTable();
    var filas = table.rows({ filter: 'applied' });
    if (filas.count() === 0) {
        alert('No hay datos en la tabla. Ajusta los filtros.');
        return;
    }

    // Color naranja de marca EPM (reemplaza el naranja neón #ff7800)
    var NARANJA_EPM = '#d56b00';

    // ¿Está activada la agrupación de críticas? (Punto 1c)
    var agrupar = document.getElementById('chkAgruparCriticas').checked;

    // Ventana de fechas activa en los filtros (Punto 1b: recorte del período)
    var fFiltroIni = cleanDate(document.getElementById('filtroInicio').value);
    var fFiltroFin = cleanDate(document.getElementById('filtroFin').value);

    // Formatea una fecha a texto YYYY-MM-DD
    function fmtFecha(d){ return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }

    /* Devuelve el período a mostrar y una nota aclaratoria con la fecha real
       SOLO cuando difiere de la ventana:
         - Sin filtro de fechas  -> período real completo, sin nota.
         - Con filtro            -> período recortado a la ventana; si el trazado
           empezó antes y/o termina después, se añade una nota pequeña con la
           vigencia real. */
    function calcularPeriodo(iniStr, finStr) {
        if (!iniStr || iniStr === 'N/A') return { texto: 'Sin fechas definidas', nota: '' };
        var ini = cleanDate(iniStr), fin = cleanDate(finStr);
        var iniReal = ini, finReal = fin;
        var recortoIni = false, recortoFin = false;

        if (fFiltroIni && ini && ini < fFiltroIni) { ini = fFiltroIni; recortoIni = true; }
        if (fFiltroFin && fin && fin > fFiltroFin) { fin = fFiltroFin; recortoFin = true; }

        var texto = (ini ? fmtFecha(ini) : iniStr) + ' → ' + (fin ? fmtFecha(fin) : finStr);

        var nota = '';
        if (recortoIni || recortoFin) {
            var real = (iniReal ? fmtFecha(iniReal) : iniStr) + ' → ' + (finReal ? fmtFecha(finReal) : finStr);
            var marca = recortoIni && recortoFin ? '↔' : (recortoIni ? '←' : '→');
            nota = '<div class="critico-nota-real">' + marca + ' Vigencia real del trazado: ' + real + '</div>';
        }
        return { texto: texto, nota: nota };
    }

    var totalReg = filas.count(), criticos = 0;
    var contratosSet = new Set();
    var minDate = null, maxDate = null;
    var pdfRows = '', progressHTML = '';
    var hoy = new Date();

    // Recolectamos las críticas aparte, para poder agruparlas después (Punto 1c)
    var listaCriticas = [];

    filas.data().each(function(row) {
        var esCritico = (row[6] || '').toUpperCase().includes('CRÍTIC') || (row[6] || '').toUpperCase().includes('CRITIC');
        if (esCritico) criticos++;
        if (row[1]) row[1].split(' vs ').forEach(function(c){ contratosSet.add(c.trim()); });

        var dIni = row[8], dFin = row[9];
        var semaforo = calcularSemaforo(dFin);

        if (dIni && dIni !== 'N/A' && dFin && dFin !== 'N/A') {
            var start = cleanDate(dIni), end = cleanDate(dFin);
            if (!minDate || start < minDate) minDate = start;
            if (!maxDate || end > maxDate)   maxDate = end;

            var total = parseInt(row[10]) || 1, pct = 0;
            if (hoy >= end) pct = 100;
            else if (hoy > start) pct = Math.min(100, Math.round(Math.ceil(Math.abs(hoy - start) / 86400000) / total * 100));

            var barColor = esCritico ? NARANJA_EPM : semaforo.color;
            progressHTML += '<div class="pdf-progress-wrap">' +
                '<div class="pdf-progress-header">' +
                '<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;width:78%;">' + row[4] + '</span>' +
                '<span style="color:' + barColor + ';">' + semaforo.emoji + ' ' + pct + '%</span>' +
                '</div>' +
                '<div class="pdf-progress-bar"><div class="pdf-progress-fill" style="width:' + pct + '%;background:' + barColor + ';"></div></div>' +
                '<div style="font-size:8px;color:' + barColor + ';margin-top:1px;">' + semaforo.label + '</div>' +
                '</div>';
        }

        if (esCritico) {
            listaCriticas.push({
                contratistas: (row[2] || 'N/A').split(' vs ').map(function(s){ return s.trim(); }).join(' · '),
                contratos:    (row[1] || 'N/A').split(' vs ').map(function(s){ return s.trim(); }).join(' · '),
                frentes:      (row[4] || 'N/A').split(' / ').map(function(s){ return s.trim(); }).join(' · '),
                dIni: dIni, dFin: dFin, semaforo: semaforo
            });
        }

        /* PUNTO 2 del PDF: el "Detalle Completo de Registros" ahora excluye
           TANTO Cercanía como Interferencias. Solo quedan trazados normales. */
        var cat = (row[0] || '').trim().toUpperCase();
        var esNormal = !cat.includes('CERCAN') && !cat.includes('INTERFEREN') && !esCritico;
        if (esNormal) {
            var colorF = semaforo.color;
            var per = calcularPeriodo(dIni, dFin);
            var celdaFechas = (dIni && dIni!=='N/A') ? per.texto + per.nota : 'N/A';
            pdfRows += '<tr>' +
                '<td>' + (row[0] || 'N/A') + '</td>' +
                '<td>' + (row[1] || 'N/A') + '</td>' +
                '<td>' + (row[2] || 'N/A') + '</td>' +
                '<td>' + (row[4] || 'N/A') + '</td>' +
                '<td>' + (row[6] || 'N/A') + '</td>' +
                '<td>' + (row[7] || 'N/A') + '</td>' +
                '<td>' + celdaFechas + '</td>' +
                '<td style="color:' + colorF + ';font-weight:bold;text-align:center;">' + semaforo.emoji + ' ' + semaforo.label + '</td>' +
                '</tr>';
        }
    });

    /* =====================================================================
       CONSTRUCCIÓN DE LAS TARJETAS CRÍTICAS
       - Orden: Contratistas -> Contratos -> Frentes -> Período (Punto 1a)
       - Período recortado a la ventana de fechas del filtro (Punto 1b)
       - Agrupación por mismo Contratista + Contrato + mismas fechas exactas,
         uniendo los distintos Frentes en una sola tarjeta (Punto 1c)
       ===================================================================== */
    function tarjetaCritica(contratistas, contratos, frentes, dIni, dFin, semaforo, notaFrentes) {
        var per = calcularPeriodo(dIni, dFin);
        return '<div class="critico-card">' +
            '<div class="critico-card-header">' +
            '<span class="critico-card-badge">⚠ Interferencia Crítica</span>' +
            '<span class="critico-card-title">' + contratistas + '</span>' +
            '</div>' +
            '<div class="critico-card-grid">' +
            '<div style="grid-column:1/-1;"><div class="critico-field-label">Contratistas involucrados</div><div class="critico-field-value">' + contratistas + '</div></div>' +
            '<div style="grid-column:1/-1;"><div class="critico-field-label">Contratos involucrados</div><div class="critico-field-value">' + contratos + '</div></div>' +
            '<div style="grid-column:1/-1;"><div class="critico-field-label">Frentes que se interfieren</div><div class="critico-field-value">' + frentes + (notaFrentes || '') + '</div></div>' +
            '</div>' +
            '<div class="critico-fechas-bar">📅 Período: <strong>' + per.texto + '</strong> &nbsp;|&nbsp; ' + semaforo.emoji + ' Vigencia: <strong>' + semaforo.label + '</strong>' + per.nota + '</div>' +
            '</div>';
    }

    var criticosHTML = '';
    if (agrupar) {
        // Agrupamos por Contratistas + Contratos + fechas exactas de inicio y fin
        var grupos = {};
        listaCriticas.forEach(function(c) {
            var clave = c.contratistas + '||' + c.contratos + '||' + c.dIni + '||' + c.dFin;
            if (!grupos[clave]) grupos[clave] = { base: c, frentes: [] };
            c.frentes.split(' · ').forEach(function(f){
                if (grupos[clave].frentes.indexOf(f) === -1) grupos[clave].frentes.push(f);
            });
        });
        Object.keys(grupos).forEach(function(clave) {
            var g = grupos[clave], c = g.base;
            var nota = g.frentes.length > 2
                ? '<div class="critico-agrupada-nota">' + g.frentes.length + ' frentes agrupados en el mismo contratista, contrato y período.</div>'
                : '';
            criticosHTML += tarjetaCritica(c.contratistas, c.contratos, g.frentes.join(' · '), c.dIni, c.dFin, c.semaforo, nota);
        });
    } else {
        listaCriticas.forEach(function(c) {
            criticosHTML += tarjetaCritica(c.contratistas, c.contratos, c.frentes, c.dIni, c.dFin, c.semaforo, '');
        });
    }

    if (!progressHTML) progressHTML = '<i style="font-size:10px;">No hay trazados con fechas válidas.</i>';
    if (!pdfRows) pdfRows = '<tr><td colspan="8" style="text-align:center;font-style:italic;color:#868e96;">No hay trazados normales en la selección actual.</td></tr>';

    var secCrit = document.getElementById('pdf-criticos-section');
    secCrit.style.display = criticos > 0 ? 'block' : 'none';
    document.getElementById('pdf-criticos-container').innerHTML = criticosHTML;

    var dateR = minDate && maxDate
        ? minDate.toLocaleDateString('es-CO') + ' al ' + maxDate.toLocaleDateString('es-CO')
        : 'Sin fechas definidas';

    document.getElementById('pdf-date-gen').innerText   = 'Generado el: ' + new Date().toLocaleString('es-CO');
    document.getElementById('pdf-total-reg').innerText  = totalReg;
    document.getElementById('pdf-total-crit').innerText = criticos;
    document.getElementById('pdf-total-cont').innerText = contratosSet.size;
    document.getElementById('pdf-date-range').innerText = dateR;

    var alertHTML = criticos > 0
        ? '<br><br><span style="color:' + NARANJA_EPM + ';font-weight:bold;">⚠️ ALERTA DE GESTIÓN:</span> Se detectaron <strong>' + criticos + ' interferencias críticas</strong> por solapamiento de fechas e infraestructura. Ver detalle en sección específica.'
        : '';

    document.getElementById('pdf-executive-summary').innerHTML =
        'El presente documento resume la gestión e interacción de Planes de Manejo de Tránsito (PMT) en el Visor Institucional. Se monitorean <strong>' + contratosSet.size + ' contratos</strong> y <strong>' + totalReg + ' frentes/interferencias</strong> operativas.' + alertHTML;

    document.getElementById('pdf-progress-container').innerHTML = progressHTML;
    document.getElementById('pdf-table-body').innerHTML         = pdfRows;

    aplicarImagenMapaEnInforme();   // muestra la imagen del mapa si el usuario la adjuntó

    document.getElementById('pdfModal').style.display = 'flex';

    // Al cambiar el interruptor de agrupación, se regenera la vista previa al instante
    var chk = document.getElementById('chkAgruparCriticas');
    chk.onchange = function() { openPdfPreview(); };
}

function closePdfPreview() {
    document.getElementById('pdfModal').style.display = 'none';
}

/* =========================================================================
   DESCARGA DEL PDF
   ========================================================================= */
function downloadPDF() {
    var opt = {
        margin:     [10, 0, 10, 0],
        filename:   'Informe_PMT_EPM.pdf',
        image:      { type: 'jpeg', quality: 0.98 },
        html2canvas:{ scale: 2 },
        jsPDF:      { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:  { mode: ['css', 'legacy'] }
    };

    html2pdf().set(opt).from(document.getElementById('pdf-content')).save()
        .then(function(){ closePdfPreview(); });
}
</script>
</body>
</html>
```

### A.3 — proceso_pmt_qgis.py

```python
import os
import re
from qgis.core import (QgsVectorLayer, QgsProject, QgsField, 
                       QgsLineSymbol, QgsSimpleLineSymbolLayer,
                       QgsFeature, QgsSingleSymbolRenderer, QgsFillSymbol,
                       QgsVectorLayerTemporalProperties, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory, QgsVectorFileWriter,
                       QgsMarkerSymbol, QgsWkbTypes, QgsGeometry) 
from PyQt5.QtCore import QVariant, Qt, QDate
from PyQt5.QtGui import QColor

# ============================================================
#  ⚙️  ÚNICA LÍNEA A EDITAR
#  Pega aquí la carpeta PADRE que contiene las 3 subcarpetas:
#     01_KMZ_Entrada, 02_Proyecto_QGIS y Control-y-Articulacion-de-PMTs-EPM
#  (Ver el paso 1 de las instrucciones para copiar la ruta exacta)
# ============================================================
BASE = r"C:\Users\lmarinza\PLATAFORMA_PMTs"

# ===== RUTA ACTUALIZADA (donde el programa busca los archivos .kmz) =====
RUTAS_KMZ = os.path.join(BASE, "01_KMZ_Entrada")

def crear_simbolo_carretera(color_relleno, grosor_relleno, grosor_borde=0.3):
    grosor_total = grosor_relleno + grosor_borde
    capa_fondo = QgsSimpleLineSymbolLayer()
    capa_fondo.setColor(QColor("black"))
    capa_fondo.setWidth(grosor_total)
    capa_fondo.setPenJoinStyle(Qt.RoundJoin)
    capa_frente = QgsSimpleLineSymbolLayer()
    capa_frente.setColor(QColor(color_relleno))
    capa_frente.setWidth(grosor_relleno)
    capa_frente.setPenJoinStyle(Qt.RoundJoin)
    simbolo = QgsLineSymbol()
    simbolo.changeSymbolLayer(0, capa_fondo)
    simbolo.appendSymbolLayer(capa_frente)
    return simbolo

def extraer_fecha_y_hora(texto):
    if not texto or texto == "No definido": return "N/A", ""
    t = str(texto).strip()
    f_match = re.search(r'\d{4}-\d{2}-\d{2}', t)
    h_match = re.search(r'\d{2}:\d{2}(:\d{2})?', t)
    f = f_match.group(0) if f_match else "N/A"
    h = h_match.group(0) if h_match else ""
    return f, h

def determinar_horario(hora_i, hora_f):
    if not hora_i and not hora_f: return "24 horas"
    try:
        hi = int(hora_i[:2]) if hora_i else 0
        hf = int(hora_f[:2]) if hora_f else 23
        if (18 <= hi <= 23) or (0 <= hi <= 3) or (18 <= hf <= 23) or (0 <= hf <= 4): return "Nocturno"
        elif 4 <= hi <= 17: return "Diurno"
    except: pass
    return "24 horas"

def procesar_todo_el_sistema():
    print("🚀 Iniciando Proceso Maestro...")
    instance = QgsProject.instance()
    
    for nombre in ["🟠 INTERFERENCIA REAL", "🔵 CERCANÍA (120m)", "📍 INGRESO Y SALIDA", "📋 REPORTE DINÁMICO", "🚀 GESTIÓN PMT MAESTRA"]:
        for c in instance.mapLayersByName(nombre): instance.removeMapLayer(c)

    capa_maestra = QgsVectorLayer("LineString?crs=EPSG:4326", "🚀 GESTIÓN PMT MAESTRA", "memory")
    prov_m = capa_maestra.dataProvider()
    prov_m.addAttributes([
        QgsField("kmz_origen", QVariant.String), QgsField("frente", QVariant.String), 
        QgsField("contrato", QVariant.String), QgsField("contratista", QVariant.String), 
        QgsField("municipio", QVariant.String), QgsField("direccion", QVariant.String), 
        QgsField("proyecto", QVariant.String), QgsField("fecha_inicio", QVariant.Date), 
        QgsField("fecha_fin", QVariant.Date), QgsField("tipo_cierre", QVariant.String)
    ])
    capa_maestra.updateFields()

    capas_alerta = {}
    campos_interferencia = [
        QgsField("CONTRATOS", QVariant.String), QgsField("FRENTES", QVariant.String), 
        QgsField("TIPO", QVariant.String), QgsField("fecha_inicio", QVariant.Date), 
        QgsField("fecha_fin", QVariant.Date)
    ]
    for clave, nombre, color in [("NARANJA", "🟠 INTERFERENCIA REAL", QColor(255, 120, 0)), ("AZUL", "🔵 CERCANÍA (120m)", QColor(0, 100, 255))]:
        capa = QgsVectorLayer("Polygon?crs=EPSG:4326", nombre, "memory")
        capa.dataProvider().addAttributes(campos_interferencia)
        capa.updateFields()
        capa.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({'color': f'{color.red()},{color.green()},{color.blue()},160', 'outline_color': 'white', 'outline_width': '0.7'})))
        capas_alerta[clave] = capa

    # ===== NUEVA CAPA: puntos azules circulares para "Ingreso y Salida" (accesos) =====
    capa_accesos = QgsVectorLayer("Point?crs=EPSG:4326", "📍 INGRESO Y SALIDA", "memory")
    prov_acc = capa_accesos.dataProvider()
    prov_acc.addAttributes([
        QgsField("kmz_origen", QVariant.String), QgsField("frente", QVariant.String),
        QgsField("contrato", QVariant.String), QgsField("contratista", QVariant.String),
        QgsField("municipio", QVariant.String), QgsField("direccion", QVariant.String),
        QgsField("proyecto", QVariant.String), QgsField("fecha_inicio", QVariant.Date),
        QgsField("fecha_fin", QVariant.Date), QgsField("tipo_cierre", QVariant.String)
    ])
    capa_accesos.updateFields()
    capa_accesos.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({
        'name': 'circle', 'color': '0,102,204', 'outline_color': 'white',
        'outline_width': '0.4', 'size': '3.5'
    })))

    capa_reporte = QgsVectorLayer("None", "📋 REPORTE DINÁMICO", "memory")
    campos_reporte = [
        QgsField("CATEGORIA", QVariant.String), QgsField("CONTRATO", QVariant.String),
        QgsField("CONTRATISTA", QVariant.String), QgsField("MUNICIPIO", QVariant.String), 
        QgsField("FRENTE", QVariant.String), QgsField("DIRECCION", QVariant.String), 
        QgsField("ESTADO_CIERRE", QVariant.String), QgsField("HORARIO", QVariant.String),
        QgsField("FECHA_INICIO", QVariant.String), QgsField("FECHA_FIN", QVariant.String), 
        QgsField("DURACION_DIAS", QVariant.Int)
    ]
    capa_reporte.dataProvider().addAttributes(campos_reporte)
    capa_reporte.updateFields()

    lista_frentes = []
    if os.path.exists(RUTAS_KMZ):
        archivos = [f for f in os.listdir(RUTAS_KMZ) if f.lower().endswith('.kmz')]
        for arch in archivos:
            c_raw = QgsVectorLayer(os.path.join(RUTAS_KMZ, arch), "raw", "ogr")
            for f in c_raw.getFeatures():
                desc = str(f.attribute('description')) if f.attribute('description') else ""
                def ex(c, t):
                    r = re.search(rf"{c}:\s*([^|]+)", t, re.IGNORECASE)
                    return r.group(1).strip() if r else "No definido"
                
                f_nom = str(f.attribute('Name')) or "Sin Nombre"
                cont, contratista, mun = ex("contrato", desc), ex("contratista", desc), ex("municipio", desc)
                f_i_raw, f_f_raw = ex("fecha_inicio", desc), ex("fecha_fin", desc)
                t_cierre, dire = ex("tipo_cierre", desc).upper(), ex("direccion", desc)
                
                f_i_clean, h_i = extraer_fecha_y_hora(f_i_raw)
                f_f_clean, h_f = extraer_fecha_y_hora(f_f_raw)
                horario_calc = determinar_horario(h_i, h_f)
                
                d_ini = QDate.fromString(f_i_clean, "yyyy-MM-dd") if f_i_clean != "N/A" else QDate()
                d_fin = QDate.fromString(f_f_clean, "yyyy-MM-dd") if f_f_clean != "N/A" else QDate()
                duracion = d_ini.daysTo(d_fin) if d_ini.isValid() and d_fin.isValid() else 0
                
                nf = QgsFeature(f)
                nf.setAttributes([arch, f_nom, cont, contratista, mun, dire, ex("proyecto", desc), d_ini, d_fin, t_cierre])
                prov_m.addFeature(nf)

                # ===== "Ingreso y Salida" -> punto azul circular (si es línea, usa su centro) =====
                if t_cierre == "INGRESO Y SALIDA":
                    g_pto = f.geometry()
                    if g_pto and not g_pto.isEmpty():
                        if g_pto.type() != QgsWkbTypes.PointGeometry:
                            g_pto = g_pto.centroid()
                        nf_acc = QgsFeature()
                        nf_acc.setGeometry(g_pto)
                        nf_acc.setAttributes([arch, f_nom, cont, contratista, mun, dire, ex("proyecto", desc), d_ini, d_fin, t_cierre])
                        prov_acc.addFeature(nf_acc)
                
                f_rep = QgsFeature()
                f_rep.setAttributes(["Trazado Normal", cont, contratista, mun, f_nom, dire, t_cierre, horario_calc, f_i_clean, f_f_clean, duracion])
                capa_reporte.dataProvider().addFeature(f_rep)
                lista_frentes.append({'geom': f.geometry().buffer(0.0011, 5), 'frente': f_nom, 'cont': cont, 'contratista': contratista, 'ini': f_i_clean, 'fin': f_f_clean})

    capa_maestra.setRenderer(QgsCategorizedSymbolRenderer("tipo_cierre", [
        QgsRendererCategory("TOTAL", crear_simbolo_carretera("#e31a1c", 0.8), "Cierre Total"),
        QgsRendererCategory("PARCIAL", crear_simbolo_carretera("#ffff00", 0.8), "Cierre Parcial"),
        QgsRendererCategory("No definido", crear_simbolo_carretera("#969696", 0.8), "Otros")
    ]))
    
    for i in range(len(lista_frentes)):
        for j in range(i + 1, len(lista_frentes)):
            f1, f2 = lista_frentes[i], lista_frentes[j]
            
            if f1['cont'] == f2['cont']: continue 

            if f1['geom'].intersects(f2['geom']):
                inter_geom = f1['geom'].intersection(f2['geom'])
                d1_i, d1_f = QDate.fromString(f1['ini'], "yyyy-MM-dd"), QDate.fromString(f1['fin'], "yyyy-MM-dd")
                d2_i, d2_f = QDate.fromString(f2['ini'], "yyyy-MM-dd"), QDate.fromString(f2['fin'], "yyyy-MM-dd")
                solapa, dias, f_ini_c, f_fin_c = False, 0, "N/A", "N/A"
                
                min_ini = d1_i if d1_i < d2_i else d2_i
                max_fin = d1_f if d1_f > d2_f else d2_f
                ini_c_date, fin_c_date = min_ini, max_fin

                if d1_i.isValid() and d1_f.isValid() and d2_i.isValid() and d2_f.isValid():
                    if d1_i <= d2_f and d2_i <= d1_f:
                        ini_c_date = d1_i if d1_i > d2_i else d2_i
                        fin_c_date = d1_f if d1_f < d2_f else d2_f
                        solapa, dias, f_ini_c, f_fin_c = True, ini_c_date.daysTo(fin_c_date) + 1, ini_c_date.toString("yyyy-MM-dd"), fin_c_date.toString("yyyy-MM-dd")

                if solapa:
                    tipo = "INTERFERENCIA REAL (CRÍTICA)"
                    f_inter = QgsFeature()
                    f_inter.setGeometry(inter_geom)
                    f_inter.setAttributes([f"{f1['cont']} vs {f2['cont']}", f"{f1['frente']} / {f2['frente']}", tipo, ini_c_date, fin_c_date])
                    capas_alerta['NARANJA'].dataProvider().addFeature(f_inter)
                    
                    f_rep_inter = QgsFeature()
                    f_rep_inter.setAttributes(["Interferencia", f"{f1['cont']} vs {f2['cont']}", f"{f1['contratista']} vs {f2['contratista']}", "Varios", f"{f1['frente']} / {f2['frente']}", "Ver Mapa", tipo, "Varios", f_ini_c, f_fin_c, dias])
                    capa_reporte.dataProvider().addFeature(f_rep_inter)
                else:
                    tipo = "CERCANÍA ESPACIAL"
                    if d1_i.isValid() and d1_f.isValid():
                        f_inter1 = QgsFeature()
                        f_inter1.setGeometry(inter_geom)
                        f_inter1.setAttributes([f1['cont'], f"{f1['frente']} (Alerta: Cercano a {f2['frente']})", tipo, d1_i, d1_f])
                        capas_alerta['AZUL'].dataProvider().addFeature(f_inter1)
                    if d2_i.isValid() and d2_f.isValid():
                        f_inter2 = QgsFeature()
                        f_inter2.setGeometry(inter_geom)
                        f_inter2.setAttributes([f2['cont'], f"{f2['frente']} (Alerta: Cercano a {f1['frente']})", tipo, d2_i, d2_f])
                        capas_alerta['AZUL'].dataProvider().addFeature(f_inter2)
                        
                    f_rep_inter = QgsFeature()
                    f_rep_inter.setAttributes(["Cercanía", f"{f1['cont']} vs {f2['cont']}", f"{f1['contratista']} vs {f2['contratista']}", "Varios", f"{f1['frente']} / {f2['frente']}", "Ver Mapa", tipo, "Varios", "N/A", "N/A", 0])
                    capa_reporte.dataProvider().addFeature(f_rep_inter)

    def aplicar_propiedades_temporales(capa):
        t_props = capa.temporalProperties()
        t_props.setIsActive(True)
        t_props.setMode(QgsVectorLayerTemporalProperties.ModeFeatureDateTimeStartAndEndFromFields)
        t_props.setStartField("fecha_inicio")
        t_props.setEndField("fecha_fin")
        try:
            if hasattr(QgsVectorLayerTemporalProperties, 'IncludeStartIncludeEnd'):
                t_props.setLimitMode(QgsVectorLayerTemporalProperties.IncludeStartIncludeEnd)
        except: pass

    aplicar_propiedades_temporales(capa_maestra)
    aplicar_propiedades_temporales(capa_accesos)
    aplicar_propiedades_temporales(capas_alerta['AZUL'])
    aplicar_propiedades_temporales(capas_alerta['NARANJA'])

    instance.addMapLayer(capa_maestra)
    instance.addMapLayer(capa_accesos)
    instance.addMapLayer(capas_alerta['AZUL'])
    instance.addMapLayer(capas_alerta['NARANJA'])
    instance.addMapLayer(capa_reporte)
    
    # ===== RUTA ACTUALIZADA (el CSV se guarda directamente en la carpeta de publicación) =====
    # QGIS sobrescribe este archivo en cada ejecución (reemplazo automático).
    # ===== RUTA ACTUALIZADA: el CSV se guarda directamente en la carpeta CLONADA
    # conectada con GitHub (la que sincroniza GitHub Desktop). Se sobrescribe solo. =====
    carpeta_destino = os.path.join(BASE, "Control-y-Articulacion-de-PMTs-EPM")
    if not os.path.exists(carpeta_destino): os.makedirs(carpeta_destino)
    ruta_csv = os.path.join(carpeta_destino, "reporte_dinamico.csv")
    opciones = QgsVectorFileWriter.SaveVectorOptions()
    opciones.driverName = "CSV"
    opciones.fileEncoding = "UTF-8"
    QgsVectorFileWriter.writeAsVectorFormatV2(capa_reporte, ruta_csv, instance.transformContext(), opciones)
    print(f"✅ Análisis completado. Exportado a: {ruta_csv}")

procesar_todo_el_sistema()
```

### A.4 — contratos_db.json (plantilla)

```json
[
  {
    "contrato": "CW323402",
    "contratista": "CONSORCIO_INFRAESTRUCTURA_DE_AGUAS_2024",
    "proyecto": "ORFELINATO",
    "municipios": ["Medellín"]
  },
  {
    "contrato": "CW322377",
    "contratista": "Consorcio AMT24",
    "proyecto": "AMPLIACION_TANQUES",
    "municipios": ["Medellín", "Envigado"]
  },
  {
    "contrato": "CW328120",
    "contratista": "SANEAR S.A.S",
    "proyecto": "EDIE1",
    "municipios": ["Medellín"]
  }
]
```

### A.5 — CLAUDE.md

```markdown
# CLAUDE.md — Plataforma de Control y Articulación de PMTs (Grupo EPM)

> Este archivo es la memoria del proyecto: Claude Code lo lee al inicio de cada sesión.
> El contexto completo (decisiones, límites, historial) está en `DOCUMENTACION_Plataforma_PMTs_EPM.md`. **Léelo antes de cambios grandes.**

## Idioma y comunicación
- Responde SIEMPRE en **español**.
- La usuaria (Leydi Marín, Centro de Gestión Servicios Técnicos de EPM) **no es programadora**: explica cada cambio en lenguaje sencillo, sin jerga innecesaria, y di qué archivo tocaste y por qué.
- Cuando entregues archivos, déjalos listos para copiar/pegar y súbelos por GitHub Desktop (ella no usa terminal).

## Objetivo de la herramienta
Automatizar el control de los Planes de Manejo de Tránsito (PMTs): capturar datos de trazados de forma estandarizada, detectar interferencias y cercanías espacio-temporales entre contratos, y visualizarlas en un dashboard web con mapa, filtros e informe PDF.

## Componentes y archivos (nombres definitivos)
- `Generador_KMZ.html` — captura estandarizada + genera KMZ (Leaflet + JSZip). Autocontenido.
- `proceso_pmt_qgis.py` — motor de análisis; se pega en la Consola de Python de QGIS. Genera capas + `reporte_dinamico.csv`.
- `Plataforma_PMTs.html` — dashboard (Bootstrap + DataTables + Select2). Lee `reporte_dinamico.csv`.
- `contratos_db.json` — base maestra de contratos (contrato → contratista, proyecto, municipios[]).
- `DOCUMENTACION_Plataforma_PMTs_EPM.md` — documento maestro con todo el detalle.

Repo publicado: `ACGST-EPM/Control-y-Articulacion-de-PMTs-EPM` (GitHub Pages).
Carpeta local: `C:\Users\lmarinza\PLATAFORMA_PMTs` (subcarpetas: `01_KMZ_Entrada`, `02_Proyecto_QGIS`, `Control-y-Articulacion-de-PMTs-EPM`).

## Invariantes que NO debes romper (si cambias una punta, actualiza la otra)
- **Formato del campo Descripción del KMZ** (lo produce el generador y lo lee el motor):
  `fecha_inicio: AAAA-MM-DD HH:MM:SS | fecha_fin: ... | tipo_cierre: <total|parcial|ingreso y salida> | direccion: ... | municipio: ... | contrato: ... | contratista: ... | proyecto: ...`
  Separador ` | `. Los textos libres eliminan cualquier `|` interno.
- **Lista cerrada `tipo_cierre`**: `total`, `parcial`, `ingreso y salida`.
- **Columnas del CSV** (`reporte_dinamico.csv`): `CATEGORIA, CONTRATO, CONTRATISTA, MUNICIPIO, FRENTE, DIRECCION, ESTADO_CIERRE, HORARIO, FECHA_INICIO, FECHA_FIN, DURACION_DIAS`. El dashboard depende de estos índices (0..10).
- **Capas QGIS** (nombres exactos): `🚀 GESTIÓN PMT MAESTRA`, `📍 INGRESO Y SALIDA` (punto azul), `🔵 CERCANÍA (120m)`, `🟠 INTERFERENCIA REAL`, `📋 REPORTE DINÁMICO`.
- **Marca EPM**: verde `#009300`, lima `#b7c200`, naranja `#d56b00`.

## Cómo debes trabajar (usa todo tu potencial)
- Sé proactivo y ambicioso: **investiga en la web** el estado actual de librerías/servicios antes de recomendar (no confíes solo en memoria), **audita** el código en busca de errores o riesgos, y **propón e implementa mejoras** alineadas al objetivo.
- Usa los **skills** que apliquen (p. ej. diseño frontend para la UI, documentos para informes, hojas de cálculo/PDF si se requieren) sin que haya que pedírtelo.
- **Verifica siempre** lo que produces: revisa sintaxis, simula la lógica con casos de prueba y confirma que no rompiste nada existente antes de decir "listo".
- Mantén el sistema de diseño y la marca EPM; conserva la coherencia entre generador, motor y dashboard.
- Planifica primero en pasos claros cuando el cambio sea grande, y explícalos.

## No hagas (don'ts)
- No incrustes llaves/secretos (API keys, contraseñas) en código de cliente (HTML/JS): el sitio es público.
- No prometas seguridad que un sitio estático no puede dar (ver SEGURIDAD abajo); sé honesto sobre los límites.
- No cambies el formato de Descripción ni las columnas del CSV sin actualizar a la vez el productor y el consumidor.
- No hagas cambios destructivos o irreversibles sin explicarlos y pedir confirmación.
- No inventes datos: si algo depende de información que no tienes, pídela o búscala.

## SEGURIDAD (workstream pendiente prioritario)
Objetivo: que solo entren correos `@epm.com.co` con un código de un solo uso que cambia en cada acceso (OTP). Un sitio estático de GitHub Pages **no** puede autenticar ni proteger los datos por sí solo. Dos rutas evaluadas: (A) **Cloudflare Access con One-time PIN** sobre Cloudflare Pages (lo más cercano al requisito, bajo código); (B) **Azure Static Web Apps con Microsoft Entra ID** (SSO corporativo; la restricción por tenant requiere plan Standard de pago). En ambos casos hay que involucrar a **TI/Seguridad de EPM** (dominio propio, gobierno de datos). Detalle completo en la sección SEGURIDAD del documento maestro.

## Verificación antes de entregar
1. ¿Sintaxis válida? (revisa/valida el JS/Python).
2. ¿La lógica hace lo esperado en casos límite? (simula).
3. ¿Se conservan las funcionalidades existentes? (sin regresiones).
4. ¿Explicaste el cambio en lenguaje sencillo y dejaste los archivos listos para subir?
```

---

*Fin del documento maestro.*
