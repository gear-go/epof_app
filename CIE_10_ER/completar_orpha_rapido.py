#!/usr/bin/env python3
"""
Completador de números ORPHA - Versión simplificada y rápida
"""

import pandas as pd
import requests
import xmltodict
from thefuzz import process, fuzz
import re

def obtener_diccionario_orpha():
    """
    Descarga y crea diccionario de nombres -> números ORPHA desde Orphanet
    """
    print("🔄 Descargando datos de Orphanet...")
    
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
            print("❌ No se encontró URL del archivo XML")
            return None

        print("🔄 Descargando XML...")
        xml_response = requests.get(xml_url, timeout=120)
        xml_response.raise_for_status()
        
        print("🔄 Parseando XML...")
        data = xmltodict.parse(xml_response.content)
        
        # Extraer disorders
        disorders = data.get('JDBOR', {}).get('DisorderList', {}).get('Disorder', [])
        print(f"📊 Total disorders encontrados: {len(disorders)}")
        
        # Crear diccionario
        diccionario = {}
        contador = 0
        
        for disorder in disorders:
            if not isinstance(disorder, dict):
                continue
                
            orpha_code = disorder.get('OrphaCode')
            if not orpha_code:
                continue
                
            # Nombre oficial
            name_obj = disorder.get('Name', {})
            if isinstance(name_obj, dict) and '#text' in name_obj:
                nombre = name_obj['#text']
                if nombre:
                    nombre_limpio = limpiar_nombre(nombre)
                    if nombre_limpio:
                        diccionario[nombre_limpio] = orpha_code
                        contador += 1
            
            # Sinónimos
            synonym_list = disorder.get('SynonymList', {})
            if synonym_list and isinstance(synonym_list, dict):
                synonyms = synonym_list.get('Synonym', [])
                if not isinstance(synonyms, list):
                    synonyms = [synonyms]
                
                for syn in synonyms:
                    if isinstance(syn, dict) and '#text' in syn:
                        syn_text = syn['#text']
                        if syn_text:
                            syn_limpio = limpiar_nombre(syn_text)
                            if syn_limpio:
                                diccionario[syn_limpio] = orpha_code
                                contador += 1
        
        print(f"✅ Diccionario creado: {contador} entradas, {len(set(diccionario.values()))} códigos únicos")
        return diccionario
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def limpiar_nombre(nombre):
    """Limpia y normaliza nombres"""
    if not nombre or pd.isna(nombre):
        return ""
    
    nombre = str(nombre).strip()
    
    # Reemplazos comunes
    reemplazos = {
        'Sindrome': 'Síndrome',
        'sindrome': 'síndrome',
        'Déficit': 'Deficiencia',
        'déficit': 'deficiencia'
    }
    
    for original, normalizado in reemplazos.items():
        nombre = nombre.replace(original, normalizado)
    
    # Limpiar caracteres especiales
    nombre = re.sub(r'[^\w\sáéíóúñü-]', '', nombre)
    nombre = ' '.join(nombre.split())
    
    return nombre

def main():
    archivo_entrada = 'homologacion_orphanet_final_20250702_075313.csv'
    
    print("🚀 COMPLETADOR DE NÚMEROS ORPHA - VERSIÓN RÁPIDA")
    print("=" * 60)
    
    # Cargar archivo
    try:
        df = pd.read_csv(archivo_entrada)
        print(f"📊 Archivo cargado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return
    
    # Obtener diccionario ORPHA
    diccionario_orpha = obtener_diccionario_orpha()
    if not diccionario_orpha:
        print("❌ No se pudo crear el diccionario ORPHA")
        return
    
    # Completar números ORPHA
    print("🔄 Completando números ORPHA...")
    
    sin_orpha = df['ORPHA_Number'].isna() | (df['ORPHA_Number'] == '') | (df['ORPHA_Number'] == 'nan')
    registros_sin_orpha = df[sin_orpha]
    print(f"🔍 Registros sin ORPHA: {len(registros_sin_orpha)}")
    
    contador_encontrados = 0
    
    for idx, row in registros_sin_orpha.iterrows():
        nombre_orphanet = row['Nombre_Orphanet']
        nombre_limpio = limpiar_nombre(nombre_orphanet)
        
        # Búsqueda exacta
        orpha_code = diccionario_orpha.get(nombre_limpio)
        
        # Si no encuentra, usar fuzzy matching
        if not orpha_code:
            result = process.extractOne(
                nombre_limpio, 
                diccionario_orpha.keys(), 
                scorer=fuzz.token_set_ratio
            )
            
            if result and result[1] >= 90:  # Umbral alto
                orpha_code = diccionario_orpha[result[0]]
        
        if orpha_code:
            df.at[idx, 'ORPHA_Number'] = orpha_code
            df.at[idx, 'ORPHA_URL'] = f"https://www.orpha.net/es/disease/detail/{orpha_code}"
            contador_encontrados += 1
    
    # Guardar resultado
    archivo_salida = archivo_entrada.replace('.csv', '_con_orpha.csv')
    df.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    # Estadísticas finales
    total_con_orpha = (~df['ORPHA_Number'].isna()) & (df['ORPHA_Number'] != '') & (df['ORPHA_Number'] != 'nan')
    
    print("=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)
    print(f"✅ Números ORPHA agregados: {contador_encontrados}")
    print(f"📈 Total con ORPHA: {total_con_orpha.sum()}/{len(df)}")
    print(f"🎯 Porcentaje completado: {(total_con_orpha.sum()/len(df))*100:.1f}%")
    print(f"📁 Archivo guardado: {archivo_salida}")
    print("=" * 60)

if __name__ == '__main__':
    main()
