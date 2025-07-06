#!/usr/bin/env python3
"""
Extractor de números ORPHA desde el XML de Orphanet
Solución eficiente para completar los números ORPHA faltantes
"""

import pandas as pd
import requests
import xmltodict
from thefuzz import process, fuzz
import re

def descargar_datos_orphanet_completos():
    """
    Descarga y procesa los datos completos de Orphanet incluyendo números ORPHA
    """
    print("🔄 Descargando datos completos de Orphanet...")
    try:
        # Obtener la URL del archivo XML
        meta_url = "http://www.orphadata.org/cgi-bin/free_product1_cross_xml.json"
        meta_response = requests.get(meta_url, timeout=60)
        meta_response.raise_for_status()
        meta_list = meta_response.json()

        # Buscar archivo en español
        xml_url = None
        for item in meta_list:
            if isinstance(item, dict) and item.get('aLanguage') == 'Spanish':
                xml_url = item.get('anUrl')
                break
        
        if not xml_url:
            print("❌ No se encontró URL del archivo XML en español")
            return None

        print(f"🔗 Descargando: {xml_url}")
        xml_response = requests.get(xml_url, timeout=120)
        xml_response.raise_for_status()
        
        # Parsear XML
        data = xmltodict.parse(xml_response.content)
        print("✅ Datos XML descargados y parseados")
        
        return data
        
    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        return None

def crear_diccionario_orpha_completo(data):
    """
    Crea un diccionario completo de nombres -> números ORPHA
    """
    print("🔄 Creando diccionario de nombres -> números ORPHA...")
    
    # Debug: verificar estructura del XML
    print("🔍 Estructura del XML:")
    print(f"   Claves principales: {list(data.keys())}")
    
    if 'JDBOR' in data:
        jdbor = data['JDBOR']
        print(f"   JDBOR claves: {list(jdbor.keys()) if isinstance(jdbor, dict) else 'No es dict'}")
        
        if 'DisorderList' in jdbor:
            disorder_list = jdbor['DisorderList']
            print(f"   DisorderList claves: {list(disorder_list.keys()) if isinstance(disorder_list, dict) else 'No es dict'}")
            
            if 'Disorder' in disorder_list:
                disorders = disorder_list['Disorder']
                print(f"   Total disorders: {len(disorders) if isinstance(disorders, list) else 'No es lista'}")
                
                # Mostrar ejemplo del primer disorder
                if isinstance(disorders, list) and len(disorders) > 0:
                    primer_disorder = disorders[0]
                    print(f"   Ejemplo disorder claves: {list(primer_disorder.keys()) if isinstance(primer_disorder, dict) else 'No es dict'}")
                    if isinstance(primer_disorder, dict):
                        print(f"   OrphaNumber: {primer_disorder.get('OrphaNumber')}")
                        if 'Name' in primer_disorder:
                            name_obj = primer_disorder['Name']
                            print(f"   Name objeto: {name_obj}")
    
    # Continuar con el parseo original pero con más debugging
    disorders = data.get('JDBOR', {}).get('DisorderList', {}).get('Disorder', [])
    
    if not disorders:
        print("❌ No se encontraron disorders en el XML")
        return {}
    
    diccionario_orpha = {}
    contador = 0
    errores = 0
    
    # Procesar solo los primeros 10 para debugging
    for i, disorder in enumerate(disorders[:10]):
        print(f"\n🔍 Procesando disorder {i+1}:")
        print(f"   Tipo: {type(disorder)}")
        print(f"   Contenido: {disorder}")
        
        orpha_number = disorder.get('OrphaCode') if isinstance(disorder, dict) else None  # Cambio de OrphaNumber a OrphaCode
        print(f"   OrphaCode extraído: {orpha_number}")
        
        nombre_oficial = None
        if isinstance(disorder, dict) and 'Name' in disorder:
            name_obj = disorder['Name']
            if isinstance(name_obj, dict) and '#text' in name_obj:
                nombre_oficial = name_obj['#text']
            elif isinstance(name_obj, str):
                nombre_oficial = name_obj
        
        print(f"   Nombre extraído: {nombre_oficial}")
        
        if orpha_number and nombre_oficial:
            nombre_limpio = limpiar_nombre(nombre_oficial)
            diccionario_orpha[nombre_limpio] = orpha_number
            contador += 1
            print(f"   ✅ Agregado: {nombre_limpio} -> {orpha_number}")
        else:
            errores += 1
            print(f"   ❌ Error: OrphaNumber={orpha_number}, Nombre={nombre_oficial}")
    
    print(f"\n📊 Debug resumen (primeros 10):")
    print(f"   Exitosos: {contador}")
    print(f"   Errores: {errores}")
    print(f"   Diccionario size: {len(diccionario_orpha)}")
    
    # Si el debug funciona, procesar todos
    if contador > 0:
        print("✅ El parseo funciona, procesando todos los disorders...")
        diccionario_orpha = {}
        contador = 0
        
        for disorder in disorders:
            orpha_number = disorder.get('OrphaCode') if isinstance(disorder, dict) else None  # Cambio de OrphaNumber a OrphaCode
            
            nombre_oficial = None
            if isinstance(disorder, dict) and 'Name' in disorder:
                name_obj = disorder['Name']
                if isinstance(name_obj, dict) and '#text' in name_obj:
                    nombre_oficial = name_obj['#text']
                elif isinstance(name_obj, str):
                    nombre_oficial = name_obj
            
            if orpha_number and nombre_oficial:
                nombre_limpio = limpiar_nombre(nombre_oficial)
                diccionario_orpha[nombre_limpio] = orpha_number
                contador += 1
                
                # Agregar sinónimos
                if 'SynonymList' in disorder and disorder['SynonymList']:
                    synonyms = disorder['SynonymList'].get('Synonym', [])
                    if not isinstance(synonyms, list):
                        synonyms = [synonyms]
                        
                    for syn in synonyms:
                        syn_text = None
                        if isinstance(syn, dict) and '#text' in syn:
                            syn_text = syn['#text']
                        elif isinstance(syn, str):
                            syn_text = syn
                            
                        if syn_text:
                            syn_limpio = limpiar_nombre(syn_text)
                            diccionario_orpha[syn_limpio] = orpha_number
                            contador += 1
    
    print(f"✅ Diccionario creado con {contador} entradas y {len(set(diccionario_orpha.values()))} números ORPHA únicos")
    return diccionario_orpha

def limpiar_nombre(nombre):
    """
    Limpia y normaliza nombres para búsqueda
    """
    if not nombre:
        return ""
    
    # Normalizar texto
    nombre = str(nombre).strip()
    
    # Reemplazos comunes
    reemplazos = {
        'Sindrome': 'Síndrome',
        'sindrome': 'síndrome',
        'Deficiencia': 'Deficiencia',
        'deficiencia': 'deficiencia',
        'Déficit': 'Deficiencia',
        'déficit': 'deficiencia'
    }
    
    for original, normalizado in reemplazos.items():
        nombre = nombre.replace(original, normalizado)
    
    # Limpiar caracteres especiales
    nombre = re.sub(r'[^\w\sáéíóúñü-]', '', nombre)
    nombre = ' '.join(nombre.split())
    
    return nombre

def encontrar_orpha_number(nombre_enfermedad, diccionario_orpha):
    """
    Encuentra el número ORPHA usando fuzzy matching
    """
    # Limpiar nombre de búsqueda
    nombre_limpio = limpiar_nombre(nombre_enfermedad)
    
    # Búsqueda exacta primero
    if nombre_limpio in diccionario_orpha:
        return diccionario_orpha[nombre_limpio]
    
    # Búsqueda fuzzy
    result = process.extractOne(
        nombre_limpio, 
        diccionario_orpha.keys(), 
        scorer=fuzz.token_set_ratio
    )
    
    if result and result[1] >= 85:  # Umbral alto para números ORPHA
        return diccionario_orpha[result[0]]
    
    return None

def completar_numeros_orpha(archivo_csv):
    """
    Completa los números ORPHA faltantes en el archivo de homologación
    """
    print(f"🔄 Cargando archivo: {archivo_csv}")
    
    try:
        df = pd.read_csv(archivo_csv)
        print(f"📊 Total de registros: {len(df)}")
        
        # Descargar datos de Orphanet
        data_orphanet = descargar_datos_orphanet_completos()
        if not data_orphanet:
            return None
            
        # Crear diccionario
        diccionario_orpha = crear_diccionario_orpha_completo(data_orphanet)
        
        # Identificar registros sin número ORPHA
        sin_orpha = df['ORPHA_Number'].isna() | (df['ORPHA_Number'] == '') | (df['ORPHA_Number'] == 'nan')
        registros_sin_orpha = df[sin_orpha]
        print(f"🔍 Registros sin número ORPHA: {len(registros_sin_orpha)}")
        
        if len(registros_sin_orpha) == 0:
            print("✅ Todos los registros ya tienen número ORPHA")
            return df
        
        contador_encontrados = 0
        contador_procesados = 0
        
        # Procesar todos los registros sin ORPHA
        for idx, row in registros_sin_orpha.iterrows():
            nombre_orphanet = row['Nombre_Orphanet']
            contador_procesados += 1
            
            if contador_procesados % 100 == 0:
                print(f"🔎 Progreso: {contador_procesados}/{len(registros_sin_orpha)}")
            
            orpha_num = encontrar_orpha_number(nombre_orphanet, diccionario_orpha)
            
            if orpha_num:
                # Actualizar el DataFrame
                df.at[idx, 'ORPHA_Number'] = orpha_num
                df.at[idx, 'ORPHA_URL'] = f"https://www.orpha.net/es/disease/detail/{orpha_num}"
                contador_encontrados += 1
        
        print(f"✅ Números ORPHA encontrados: {contador_encontrados}/{len(registros_sin_orpha)}")
        print(f"📈 Porcentaje de mejora: {(contador_encontrados/len(registros_sin_orpha))*100:.1f}%")
        
        return df
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return None

def generar_estadisticas_finales(df):
    """
    Genera estadísticas finales del archivo completado
    """
    total_registros = len(df)
    con_orpha = (~df['ORPHA_Number'].isna()) & (df['ORPHA_Number'] != '') & (df['ORPHA_Number'] != 'nan')
    total_con_orpha = con_orpha.sum()
    
    print("\n" + "=" * 50)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 50)
    print(f"📈 Total de registros: {total_registros}")
    print(f"✅ Registros con ORPHA: {total_con_orpha}")
    print(f"❌ Registros sin ORPHA: {total_registros - total_con_orpha}")
    print(f"🎯 Porcentaje completado: {(total_con_orpha/total_registros)*100:.1f}%")
    
    # Mostrar algunos ejemplos de los nuevos números ORPHA encontrados
    nuevos_con_orpha = df[con_orpha].head(10)
    print(f"\n📋 Ejemplos de registros con ORPHA:")
    for _, row in nuevos_con_orpha.iterrows():
        if pd.notna(row['ORPHA_Number']) and row['ORPHA_Number'] != '':
            print(f"   • ORPHA:{row['ORPHA_Number']} - {row['Nombre_Orphanet']}")

def main():
    archivo_entrada = 'homologacion_orphanet_final_20250702_075313.csv'
    
    print("🚀 COMPLETADOR DE NÚMEROS ORPHA")
    print("=" * 50)
    
    df_completado = completar_numeros_orpha(archivo_entrada)
    
    if df_completado is not None:
        # Guardar archivo completado
        archivo_salida = archivo_entrada.replace('.csv', '_con_orpha.csv')
        df_completado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        # Generar estadísticas
        generar_estadisticas_finales(df_completado)
        
        print("=" * 50)
        print(f"✅ Archivo completado guardado: {archivo_salida}")
        print("=" * 50)
    else:
        print("❌ No se pudo completar el archivo")

if __name__ == '__main__':
    main()
