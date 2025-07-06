#!/usr/bin/env python3
"""
Corrector de números ORPHA
Busca y asigna los números ORPHA faltantes en los resultados de homologación
"""

import pandas as pd
import requests
import time
import re
from urllib.parse import quote

def buscar_orpha_number(nombre_enfermedad):
    """
    Busca el número ORPHA de una enfermedad mediante búsqueda web
    """
    try:
        # Limpiar nombre para búsqueda
        nombre_limpio = nombre_enfermedad.replace('Síndrome', '').replace('síndrome', '').strip()
        
        # URL de búsqueda en Orphanet
        url_busqueda = f"https://www.orpha.net/consor/cgi-bin/Disease_Search.php?lng=ES&search_type=simple&search_value={quote(nombre_limpio)}"
        
        # Headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_busqueda, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Buscar patrones de números ORPHA en la respuesta
            patron_orpha = r'ORPHA:(\d+)'
            matches = re.findall(patron_orpha, response.text)
            
            if matches:
                return matches[0]  # Retornar el primer match
                
    except Exception as e:
        print(f"Error buscando {nombre_enfermedad}: {e}")
    
    return None

def corregir_numeros_orpha(archivo_csv):
    """
    Corrige los números ORPHA faltantes en el archivo de homologación
    """
    print(f"🔄 Cargando archivo: {archivo_csv}")
    
    try:
        df = pd.read_csv(archivo_csv)
        print(f"📊 Total de registros: {len(df)}")
        
        # Encontrar registros sin número ORPHA
        sin_orpha = df['ORPHA_Number'].isna() | (df['ORPHA_Number'] == '')
        registros_sin_orpha = df[sin_orpha]
        print(f"🔍 Registros sin número ORPHA: {len(registros_sin_orpha)}")
        
        if len(registros_sin_orpha) == 0:
            print("✅ Todos los registros ya tienen número ORPHA")
            return df
        
        # Procesar una muestra (primeros 50 para no saturar el servidor)
        muestra = min(50, len(registros_sin_orpha))
        print(f"🎯 Procesando muestra de {muestra} registros...")
        
        contador_encontrados = 0
        
        for i, (idx, row) in enumerate(registros_sin_orpha.head(muestra).iterrows()):
            nombre_orphanet = row['Nombre_Orphanet']
            print(f"🔎 [{i+1}/{muestra}] Buscando: {nombre_orphanet}")
            
            orpha_num = buscar_orpha_number(nombre_orphanet)
            
            if orpha_num:
                # Actualizar el DataFrame
                df.at[idx, 'ORPHA_Number'] = orpha_num
                df.at[idx, 'ORPHA_URL'] = f"https://www.orpha.net/es/disease/detail/{orpha_num}"
                contador_encontrados += 1
                print(f"   ✅ Encontrado: ORPHA:{orpha_num}")
            else:
                print(f"   ❌ No encontrado")
            
            # Pausa para no saturar el servidor
            time.sleep(1)
        
        print(f"🎯 Números ORPHA encontrados: {contador_encontrados}/{muestra}")
        return df
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return None

def main():
    archivo_entrada = 'homologacion_orphanet_final_20250702_075313.csv'
    
    print("🚀 CORRECTOR DE NÚMEROS ORPHA")
    print("=" * 45)
    
    df_corregido = corregir_numeros_orpha(archivo_entrada)
    
    if df_corregido is not None:
        # Guardar archivo corregido
        archivo_salida = archivo_entrada.replace('.csv', '_corregido.csv')
        df_corregido.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print("=" * 45)
        print(f"✅ Archivo corregido guardado: {archivo_salida}")
        
        # Estadísticas finales
        total_con_orpha = (~df_corregido['ORPHA_Number'].isna()) & (df_corregido['ORPHA_Number'] != '')
        print(f"📊 Registros con número ORPHA: {total_con_orpha.sum()}/{len(df_corregido)}")
    else:
        print("❌ No se pudo procesar el archivo")

if __name__ == '__main__':
    main()
