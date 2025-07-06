import requests
import zipfile
import io
import xmltodict
import pandas as pd
from thefuzz import process, fuzz
from datetime import datetime
import os
import sys
import re

def descargar_y_procesar_orphanet(product_id="product1"):
    """
    Descarga y procesa los datos de enfermedades raras desde Orphadata.
    Utiliza los ficheros "free products" para obtener la información más completa y actualizada.
    """
    print(f"🔄 Descargando y procesando datos de Orphanet (producto: {product_id})...")
    try:
        # Obtener la URL del archivo XML desde los metadatos
        meta_url = f"http://www.orphadata.org/cgi-bin/free_{product_id}_cross_xml.json"
        meta_response = requests.get(meta_url, timeout=60)
        meta_response.raise_for_status()
        meta_list = meta_response.json()

        # Buscar la URL del archivo en español
        xml_url = None
        version_date = 'N/A'
        for item in meta_list:
            if isinstance(item, dict) and item.get('aLanguage') == 'Spanish':
                xml_url = item.get('anUrl')
                version_date = item.get('aDate')
                break
        
        if not xml_url:
            print("❌ Error: No se encontró la URL para el archivo XML en español.", file=sys.stderr)
            return None, None

        print(f"🔗 URL del archivo XML: {xml_url}")
        
        # Descargar el archivo XML directamente
        xml_response = requests.get(xml_url, timeout=120)
        xml_response.raise_for_status()
        
        # Parsear el contenido XML
        data = xmltodict.parse(xml_response.content)
        
        print(f"✅ Datos de Orphanet descargados y parseados (versión: {version_date})")
        return data, version_date
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red al descargar los datos de Orphanet: {e}", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"❌ Error inesperado al procesar los datos de Orphanet: {e}", file=sys.stderr)
        return None, None

def normalizar_datos_orphanet(data):
    """
    Normaliza los datos XML de Orphanet en un DataFrame de pandas fácil de usar.
    Extrae nombres, sinónimos y códigos CIE-10.
    """
    print("🔄 Normalizando datos de Orphanet a un formato tabular...")
    disorders = data.get('JDBOR', {}).get('DisorderList', {}).get('Disorder', [])
    
    orphanet_list = []
    for disorder in disorders:
        orpha_number = disorder.get('OrphaNumber')
        nombre_oficial = disorder.get('Name', {}).get('#text')
        
        # Extraer todos los nombres y sinónimos para mejorar la búsqueda
        nombres_y_sinonimos = {nombre_oficial}
        if 'SynonymList' in disorder and disorder['SynonymList']:
            synonyms = disorder['SynonymList'].get('Synonym', [])
            if not isinstance(synonyms, list):
                synonyms = [synonyms]
            for syn in synonyms:
                nombres_y_sinonimos.add(syn.get('#text'))

        # Extraer códigos CIE-10
        codigos_cie10 = []
        if 'ExternalReferenceList' in disorder and disorder['ExternalReferenceList']:
            references = disorder['ExternalReferenceList'].get('ExternalReference', [])
            if not isinstance(references, list):
                references = [references]
            for ref in references:
                if ref.get('Source') == 'ICD-10':
                    codigos_cie10.append(ref.get('Reference'))
        
        orphanet_list.append({
            'orpha_number': orpha_number,
            'nombre_oficial': nombre_oficial,
            'nombres_y_sinonimos': list(nombres_y_sinonimos),
            'codigos_cie10_orphanet': codigos_cie10
        })
        
    df_orphanet = pd.DataFrame(orphanet_list)
    print(f"✅ Datos de Orphanet normalizados. Total: {len(df_orphanet)} enfermedades.")
    return df_orphanet

def cargar_dataset_colombia(archivo_csv):
    """Carga el dataset de enfermedades de Colombia desde un archivo CSV."""
    print(f"🔄 Cargando dataset de Colombia desde '{archivo_csv}'...")
    try:
        df = pd.read_csv(archivo_csv, encoding='utf-8')
        print(f"🔍 Columnas originales: {df.columns.tolist()}")
        
        # Mapear las columnas reales del CSV
        column_mapping = {
            'Número': 'numero',
            'Nombre_Enfermedad': 'nombre_colombia', 
            'Código_CIE10': 'codigo_cie10',
            'Observaciones': 'observaciones'
        }
        
        # Renombrar columnas
        df = df.rename(columns=column_mapping)
        
        # Limpiar datos
        df['nombre_colombia'] = df['nombre_colombia'].str.strip()
        df['codigo_cie10'] = df['codigo_cie10'].str.strip()
        
        # Agregar punto al código CIE-10 si no lo tiene (formato estándar)
        def formatear_cie10(codigo):
            if pd.isna(codigo) or codigo == '':
                return ''
            codigo = str(codigo).strip()
            # Si es formato LNNN añadir punto: Q878 -> Q87.8
            if len(codigo) == 4 and codigo[0].isalpha() and codigo[1:].isdigit():
                return f"{codigo[:3]}.{codigo[3]}"
            return codigo
            
        df['codigo_cie10_formateado'] = df['codigo_cie10'].apply(formatear_cie10)
        
        print(f"✅ Dataset de Colombia cargado: {len(df)} enfermedades.")
        print(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{archivo_csv}'", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error cargando el dataset de Colombia: {e}", file=sys.stderr)
        return None

def encontrar_mejor_match(nombre_colombia, choices_dict):
    """
    Encuentra la mejor coincidencia para un nombre de enfermedad en la lista de Orphanet.
    Utiliza múltiples estrategias de búsqueda para mejorar la precisión.
    """
    # Limpiar el nombre de búsqueda
    nombre_limpio = limpiar_nombre_enfermedad(nombre_colombia)
    
    # Estrategia 1: Búsqueda exacta (insensible a mayúsculas)
    for choice_name, choice_data in choices_dict.items():
        if choice_name.lower() == nombre_limpio.lower():
            return choice_data, 100
    
    # Estrategia 2: Búsqueda fuzzy con diferentes algoritmos
    algoritmos = [fuzz.token_set_ratio, fuzz.token_sort_ratio, fuzz.ratio]
    mejores_resultados = []
    
    for algoritmo in algoritmos:
        result = process.extractOne(nombre_limpio, choices_dict.keys(), scorer=algoritmo)
        if result:
            best_match_name = result[0]
            score = result[1]
            mejores_resultados.append((choices_dict[best_match_name], score, algoritmo.__name__))
    
    # Seleccionar el mejor resultado
    if mejores_resultados:
        mejores_resultados.sort(key=lambda x: x[1], reverse=True)
        best_data, best_score, algorithm_used = mejores_resultados[0]
        return best_data, best_score
        
    return None, 0

def limpiar_nombre_enfermedad(nombre):
    """
    Limpia y normaliza nombres de enfermedades para mejorar las coincidencias.
    """
    if not nombre or pd.isna(nombre):
        return ""
    
    # Convertir a string y limpiar
    nombre = str(nombre).strip()
    
    # Normalizar texto común
    reemplazos = {
        'Sindrome': 'Síndrome',
        'sindrome': 'síndrome', 
        'Deficiencia': 'Deficiencia',
        'deficiencia': 'deficiencia',
        'Déficit': 'Deficiencia',
        'déficit': 'deficiencia',
        'Acidemia': 'Acidemia',
        'acidemia': 'acidemia',
        'Aciduria': 'Aciduria',
        'aciduria': 'aciduria'
    }
    
    for original, normalizado in reemplazos.items():
        nombre = nombre.replace(original, normalizado)
    
    # Eliminar caracteres especiales problemáticos
    nombre = re.sub(r'[^\w\sáéíóúñü-]', '', nombre)
    
    # Normalizar espacios
    nombre = ' '.join(nombre.split())
    
    return nombre


def homologar_enfermedades(df_colombia, df_orphanet):
    """
    Realiza el proceso de homologación entre la lista de Colombia y los datos de Orphanet.
    """
    print("🔄 Iniciando proceso de homologación...")
    
    # Crear un diccionario de búsqueda optimizado para Orphanet
    # Mapea cada sinónimo a la información completa de la enfermedad
    choices_dict = {}
    for _, row in df_orphanet.iterrows():
        for name in row['nombres_y_sinonimos']:
            if name and isinstance(name, str) and len(name.strip()) > 2:
                name_clean = limpiar_nombre_enfermedad(name)
                if name_clean:
                    choices_dict[name_clean] = row.to_dict()

    print(f"📚 Diccionario de búsqueda creado con {len(choices_dict)} entradas")
    
    resultados = []
    total = len(df_colombia)
    encontrados_alta_confianza = 0
    encontrados_media_confianza = 0
    
    for index, row in df_colombia.iterrows():
        nombre_a_buscar = row['nombre_colombia']
        
        # Imprimir progreso cada 50 elementos
        if (index + 1) % 50 == 0 or index == 0:
            print(f"🔎 Progreso: {index + 1}/{total} ({((index + 1)/total)*100:.1f}%)")
        
        match_data, score = encontrar_mejor_match(nombre_a_buscar, choices_dict)
        
        # Clasificar matches por confianza
        if match_data and score >= 85:  # Alta confianza
            encontrado = True
            nivel_confianza = "Alta"
            encontrados_alta_confianza += 1
        elif match_data and score >= 70:  # Media confianza
            encontrado = True
            nivel_confianza = "Media"
            encontrados_media_confianza += 1
        elif match_data and score >= 60:  # Baja confianza (reportar pero marcar)
            encontrado = True
            nivel_confianza = "Baja"
        else:
            encontrado = False
            nivel_confianza = "No encontrado"
            
        if encontrado and match_data:
            resultado = {
                'numero_colombia': row.get('numero', ''),
                'nombre_colombia': nombre_a_buscar,
                'codigo_cie10_colombia': row.get('codigo_cie10', ''),
                'codigo_cie10_formateado': row.get('codigo_cie10_formateado', ''),
                'encontrado': True,
                'nivel_confianza': nivel_confianza,
                'orpha_number': match_data.get('orpha_number', ''),
                'nombre_orphanet': match_data.get('nombre_oficial', ''),
                'codigos_cie10_orphanet': ', '.join(match_data.get('codigos_cie10_orphanet', [])) if match_data.get('codigos_cie10_orphanet') else '',
                'similitud': round(score, 2),
                'observaciones_colombia': row.get('observaciones', '')
            }
        else:
            resultado = {
                'numero_colombia': row.get('numero', ''),
                'nombre_colombia': nombre_a_buscar,
                'codigo_cie10_colombia': row.get('codigo_cie10', ''),
                'codigo_cie10_formateado': row.get('codigo_cie10_formateado', ''),
                'encontrado': False,
                'nivel_confianza': nivel_confianza,
                'orpha_number': None,
                'nombre_orphanet': 'No encontrado',
                'codigos_cie10_orphanet': '',
                'similitud': round(score, 2) if score > 0 else 0,
                'observaciones_colombia': row.get('observaciones', '')
            }
        resultados.append(resultado)

    print(f"✅ Proceso de homologación completado.")
    print(f"📊 Resultados:")
    print(f"   • Alta confianza (≥85%): {encontrados_alta_confianza}")
    print(f"   • Media confianza (70-84%): {encontrados_media_confianza}")
    print(f"   • Total encontrados: {encontrados_alta_confianza + encontrados_media_confianza}")
    print(f"   • Total procesados: {total}")
    print(f"   • Tasa de éxito: {((encontrados_alta_confianza + encontrados_media_confianza)/total)*100:.1f}%")
    
    return pd.DataFrame(resultados)

def main():
    """Función principal para ejecutar el proceso completo."""
    
    # --- Configuración ---
    archivo_input_colombia = 'enfermedades_raras_colombia_2023_corregido.csv'
    
    print("🚀 HOMOLOGACIÓN DIRECTA ORPHANET → COLOMBIA")
    print("=" * 60)
    
    # Descargar y preparar datos de Orphanet
    orphanet_data, version_date = descargar_y_procesar_orphanet()
    if not orphanet_data:
        print("❌ No se pudieron obtener los datos de Orphanet")
        sys.exit(1)
        
    df_orphanet = normalizar_datos_orphanet(orphanet_data)
    
    # Cargar datos de Colombia
    df_colombia = cargar_dataset_colombia(archivo_input_colombia)
    if df_colombia is None:
        print("❌ No se pudo cargar el dataset de Colombia")
        sys.exit(1)
        
    # Realizar la homologación
    df_resultados = homologar_enfermedades(df_colombia, df_orphanet)
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_output = f'homologacion_orphanet_directa_{timestamp}.csv'
    
    # Ordenar por nivel de confianza y similitud
    orden_confianza = {'Alta': 1, 'Media': 2, 'Baja': 3, 'No encontrado': 4}
    df_resultados['orden_confianza'] = df_resultados['nivel_confianza'].map(orden_confianza)
    df_resultados = df_resultados.sort_values(['orden_confianza', 'similitud'], ascending=[True, False])
    df_resultados = df_resultados.drop('orden_confianza', axis=1)
    
    df_resultados.to_csv(archivo_output, index=False, encoding='utf-8-sig')
    
    # Crear resumen estadístico
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE HOMOLOGACIÓN")
    print("=" * 60)
    print(f"📅 Versión de datos de Orphanet: {version_date}")
    print(f"📁 Archivo de salida: '{archivo_output}'")
    print(f"📈 Total de enfermedades procesadas: {len(df_resultados)}")
    
    # Estadísticas por nivel de confianza
    stats = df_resultados['nivel_confianza'].value_counts()
    for nivel, count in stats.items():
        porcentaje = (count / len(df_resultados)) * 100
        print(f"   • {nivel}: {count} ({porcentaje:.1f}%)")
    
    # Estadísticas adicionales
    encontrados = df_resultados['encontrado'].sum()
    tasa_exito = (encontrados / len(df_resultados)) * 100
    print(f"\n🎯 Tasa de éxito total: {encontrados}/{len(df_resultados)} ({tasa_exito:.1f}%)")
    
    # Crear archivo de estadísticas detalladas
    archivo_stats = f'estadisticas_homologacion_{timestamp}.txt'
    with open(archivo_stats, 'w', encoding='utf-8') as f:
        f.write("ESTADÍSTICAS DETALLADAS DE HOMOLOGACIÓN\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Versión Orphanet: {version_date}\n")
        f.write(f"Total procesadas: {len(df_resultados)}\n\n")
        
        f.write("Por nivel de confianza:\n")
        for nivel, count in stats.items():
            porcentaje = (count / len(df_resultados)) * 100
            f.write(f"  {nivel}: {count} ({porcentaje:.1f}%)\n")
        
        f.write(f"\nTasa de éxito: {tasa_exito:.1f}%\n")
        
        # Top 10 mejores matches
        f.write("\nTOP 10 MEJORES COINCIDENCIAS:\n")
        top_matches = df_resultados[df_resultados['encontrado'] == True].nlargest(10, 'similitud')
        for _, row in top_matches.iterrows():
            f.write(f"  {row['similitud']:.1f}% - {row['nombre_colombia']} → {row['nombre_orphanet']}\n")
    
    print(f"📄 Estadísticas detalladas guardadas en: '{archivo_stats}'")
    print("=" * 60)
    print("✅ Proceso completado exitosamente")

if __name__ == '__main__':
    # Instalar dependencias si no están presentes
    try:
        import pandas as pd
        import requests
        import xmltodict
        from thefuzz import process, fuzz
    except ImportError:
        print("Algunas librerías no están instaladas. Intentando instalar...")
        os.system(f'{sys.executable} -m pip install pandas requests xmltodict "thefuzz[speedup]"')
        print("Librerías instaladas. Por favor, vuelve a ejecutar el script.")
        sys.exit(0)
        
    main()
