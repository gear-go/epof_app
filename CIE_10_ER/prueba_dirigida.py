#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRUEBA DIRIGIDA - Homologación de enfermedades específicas conocidas
Testa el sistema con enfermedades que sabemos que deben estar en Orphanet
"""

import pandas as pd
import requests
import time
from urllib.parse import quote
import re

def buscar_en_orphanet_simple(nombre_enfermedad):
    """Búsqueda simplificada en Orphanet"""
    try:
        # Limpiar nombre
        termino = limpiar_nombre(nombre_enfermedad)
        
        # URL de búsqueda en español
        termino_encoded = quote(termino)
        url_busqueda = f"https://www.orpha.net/es/disease/search?query={termino_encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es,en;q=0.5',
        }
        
        response = requests.get(url_busqueda, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            contenido = response.text
            
            # Buscar enlaces a páginas de detalle
            patron_enlaces = r'href="[^"]*disease/detail/(\d+)[^"]*"[^>]*>([^<]+)</a>'
            matches = re.findall(patron_enlaces, contenido, re.IGNORECASE)
            
            if matches:
                orpha_num, nombre_encontrado = matches[0]
                return {
                    'encontrado': True,
                    'orpha': orpha_num,
                    'nombre_orphanet': nombre_encontrado.strip(),
                    'url': f"https://www.orpha.net/es/disease/detail/{orpha_num}",
                    'url_busqueda': url_busqueda
                }
        
        return {
            'encontrado': False,
            'error': f'No encontrado (HTTP {response.status_code})',
            'url_busqueda': url_busqueda
        }
        
    except Exception as e:
        return {
            'encontrado': False,
            'error': str(e),
            'url_busqueda': url_busqueda if 'url_busqueda' in locals() else 'Error construyendo URL'
        }

def limpiar_nombre(nombre):
    """Limpia nombre para búsqueda"""
    # Remover prefijos comunes
    prefijos = ['síndrome de ', 'sindrome de ', 'enfermedad de ', 'deficiencia de ']
    nombre_lower = nombre.lower()
    
    for prefijo in prefijos:
        if nombre_lower.startswith(prefijo):
            nombre = nombre[len(prefijo):].strip()
            break
    
    # Limpiar caracteres especiales
    nombre = re.sub(r'[^\w\s\-]', ' ', nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    return nombre

def main():
    print("=" * 80)
    print("🎯 PRUEBA DIRIGIDA - ENFERMEDADES CONOCIDAS")
    print("=" * 80)
    
    # Enfermedades específicas que sabemos que existen
    casos_test = [
        {"nombre": "Acondroplasia", "esperado": "Debe encontrarse"},
        {"nombre": "Acidemia isovalérica", "esperado": "Debe encontrarse"},
        {"nombre": "Acromegalia", "esperado": "Debe encontrarse"},
        {"nombre": "Albinismo oculo-cutáneo", "esperado": "Debe encontrarse"},
        {"nombre": "Síndrome de Aicardi", "esperado": "Debe encontrarse"},
        {"nombre": "Síndrome de Marfan", "esperado": "Debe encontrarse"},
        {"nombre": "Fenilcetonuria", "esperado": "Debe encontrarse"},
        {"nombre": "Fibrosis quística", "esperado": "Debe encontrarse"}
    ]
    
    print(f"🔍 Probando {len(casos_test)} enfermedades conocidas...")
    print(f"⏱️  Tiempo estimado: {len(casos_test) * 1.5:.1f} segundos\n")
    
    resultados = []
    encontrados = 0
    
    for i, caso in enumerate(casos_test, 1):
        nombre = caso['nombre']
        print(f"🔍 {i}/{len(casos_test)}: {nombre}...", end=" ")
        
        resultado = buscar_en_orphanet_simple(nombre)
        
        if resultado['encontrado']:
            encontrados += 1
            print(f"✅ ORPHA:{resultado['orpha']} - {resultado['nombre_orphanet']}")
        else:
            print(f"❌ {resultado.get('error', 'No encontrado')}")
        
        resultados.append({
            'nombre_colombia': nombre,
            'encontrado': resultado['encontrado'],
            'orpha': resultado.get('orpha', ''),
            'nombre_orphanet': resultado.get('nombre_orphanet', ''),
            'url': resultado.get('url', ''),
            'url_busqueda': resultado.get('url_busqueda', ''),
            'error': resultado.get('error', '')
        })
        
        time.sleep(1.5)  # Delay entre búsquedas
    
    print(f"\n" + "=" * 80)
    print(f"📊 RESULTADOS DE PRUEBA DIRIGIDA:")
    print(f"✅ Encontradas: {encontrados}/{len(casos_test)} ({encontrados/len(casos_test)*100:.1f}%)")
    print(f"❌ No encontradas: {len(casos_test) - encontrados}")
    
    if encontrados > 0:
        print(f"\n🎯 EXITOSOS:")
        for r in resultados:
            if r['encontrado']:
                print(f"   • {r['nombre_colombia']} → ORPHA:{r['orpha']}")
    
    if encontrados < len(casos_test):
        print(f"\n❌ NO ENCONTRADOS:")
        for r in resultados:
            if not r['encontrado']:
                print(f"   • {r['nombre_colombia']}: {r['error']}")
    
    # Guardar resultados
    df_resultados = pd.DataFrame(resultados)
    archivo = "prueba_dirigida_enfermedades_conocidas.csv"
    df_resultados.to_csv(archivo, index=False, encoding='utf-8')
    
    print(f"\n📄 Resultados guardados: {archivo}")
    
    if encontrados >= len(casos_test) * 0.6:  # Si encuentra al menos 60%
        print(f"\n✅ SISTEMA FUNCIONAL - Listo para homologación masiva")
    else:
        print(f"\n⚠️  VERIFICAR CONFIGURACIÓN - Tasa de éxito baja")

if __name__ == "__main__":
    main()
