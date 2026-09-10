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
