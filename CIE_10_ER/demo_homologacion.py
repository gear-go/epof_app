#!/usr/bin/env python3
"""
DEMOSTRACIÓN DEL PROCESO DE HOMOLOGACIÓN ORPHANET
Muestra exactamente cómo funciona la búsqueda nombre → Orphanet

Proceso:
1. Toma nombre de enfermedad del CSV Colombia
2. Busca en Orphanet ese nombre
3. Extrae códigos ORPHA y CIE-10 de Orphanet
4. Compara con código CIE-10 de Colombia
"""

import pandas as pd
import requests
import time
from datetime import datetime
import re
import warnings

# Suprimir advertencias de solicitud insegura si verify=False se utiliza
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)


def demonstrar_homologacion():
    """Demuestra el proceso con ejemplos específicos"""
    print("=" * 80)
    print("🔍 DEMOSTRACIÓN: PROCESO DE HOMOLOGACIÓN ORPHANET")
    print("=" * 80)
    print("Flujo: CSV Colombia → Búsqueda Orphanet → Comparación códigos")
    print("=" * 80)
    
    # Cargar dataset Colombia
    try:
        df = pd.read_csv("enfermedades_raras_colombia_2023_corregido.csv")
    except FileNotFoundError:
        print("❌ ERROR: No se encontró el archivo 'enfermedades_raras_colombia_2023_corregido.csv'")
        print("Por favor, asegúrese de que el archivo esté en el mismo directorio que el script.")
        return

    # Ejemplos específicos para demostrar
    ejemplos = [
        {"fila": 35, "nombre": "Acondrogénesis", "codigo_colombia": "Q770"},
        {"fila": 36, "nombre": "Acondroplasia", "codigo_colombia": "Q774"}, 
        {"fila": 45, "nombre": "Acromegalia", "codigo_colombia": "E220"},
        {"fila": 6, "nombre": "Acalasia primaria", "codigo_colombia": "K220"}
    ]
    
    for i, ejemplo in enumerate(ejemplos):
        print(f"\n{'='*20} EJEMPLO {i+1}: {ejemplo['nombre']} {'='*20}")
        
        # Datos de Colombia
        print(f"📋 DATOS COLOMBIA:")
        print(f"   Nombre: {ejemplo['nombre']}")
        print(f"   Código CIE-10: {ejemplo['codigo_colombia']}")
        
        # Búsqueda en Orphanet
        print(f"\n🔍 BÚSQUEDA EN ORPHANET:")
        resultado = buscar_en_orphanet(ejemplo['nombre'])
        
        if resultado['encontrado']:
            print(f"   ✅ Encontrada en Orphanet")
            print(f"   Término búsqueda: '{resultado['termino_busqueda']}'")
            
            if resultado['codigos_orpha']:
                print(f"   🏷️  Códigos ORPHA: {sorted(list(set(resultado['codigos_orpha'])))}")
            
            if resultado['codigos_cie10']:
                print(f"   🔢 Códigos CIE-10 Orphanet: {sorted(list(set(resultado['codigos_cie10'])))}")
            
            # Comparación
            print(f"\n📊 COMPARACIÓN:")
            if ejemplo['codigo_colombia'] in resultado['codigos_cie10']:
                print(f"   🎯 COINCIDENCIA EXACTA: {ejemplo['codigo_colombia']}")
            else:
                similitud = calcular_similitud(ejemplo['codigo_colombia'], resultado['codigos_cie10'])
                print(f"   ⚖️  Similitud: {similitud*100:.1f}%")
                print(f"   Colombia: {ejemplo['codigo_colombia']} vs Orphanet: {resultado['codigos_cie10']}")
        else:
            print(f"   ❌ No encontrada en Orphanet")
            print(f"   Motivo: {resultado.get('error', 'Sin resultados específicos')}")
        
        print(f"   🌐 URL búsqueda: {resultado['url']}")
        
        time.sleep(2)  # Pausa entre búsquedas
    
    print(f"\n{'='*80}")
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("El proceso busca NOMBRES de Colombia en Orphanet,")
    print("NO busca códigos CIE-10 de Colombia en Orphanet")
    print("=" * 80)

def buscar_en_orphanet(nombre_enfermedad):
    """Realiza búsqueda real en Orphanet"""
    # Limpiar nombre para búsqueda
    termino = limpiar_nombre(nombre_enfermedad)
    
    # URL de búsqueda Orphanet
    base_url = "https://www.orpha.net/consor/cgi-bin/Disease_Search.php"
    params = {
        "lng": "EN",  # MODIFICADO: Usar inglés para búsquedas más robustas
        "data_id": "Pat", 
        "search": "Disease_Search_Simple",
        "Typ": "Pat",
        "diseaseGroup": termino
    }
    
    # Construir URL para depuración
    query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
    url_completa = f"{base_url}?{query_string}"
    
    try:
        # Usar un User-Agent común y deshabilitar la verificación SSL
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(base_url, params=params, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            # Parsear resultados
            orpha_codes = re.findall(r'ORPHA:(\d+)', response.text, re.IGNORECASE)
            icd10_codes = extraer_codigos_cie10_validos(response.text)
            
            return {
                "encontrado": len(orpha_codes) > 0 or len(icd10_codes) > 0,
                "termino_busqueda": termino,
                "codigos_orpha": [f"ORPHA:{code}" for code in orpha_codes],
                "codigos_cie10": icd10_codes,
                "url": url_completa,
                "status": response.status_code
            }
        else:
            return {
                "encontrado": False,
                "error": f"HTTP {response.status_code}",
                "url": url_completa,
                "termino_busqueda": termino
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "encontrado": False,
            "error": f"Error de conexión: {type(e).__name__}",
            "url": url_completa,
            "termino_busqueda": termino
        }

def limpiar_nombre(nombre):
    """Limpia nombre para búsqueda efectiva"""
    # Remover prefijos comunes
    prefijos = ['sindrome de ', 'síndrome de ', 'enfermedad de ']
    nombre_lower = nombre.lower()
    
    for prefijo in prefijos:
        if nombre_lower.startswith(prefijo):
            nombre = nombre[len(prefijo):].strip()
            break
    
    # Limpiar caracteres especiales
    nombre = re.sub(r'[^\w\s\-]', ' ', nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    return nombre

def extraer_codigos_cie10_validos(html_content):
    """Extrae códigos CIE-10 válidos del HTML"""
    # Patrón para códigos CIE-10 (letra, 2 dígitos, opcional punto y 1 o 2 dígitos más)
    pattern = r'\b([A-Z]\d{2}(?:\.\d{1,2})?)\b'
    codigos = re.findall(pattern, html_content)
    
    # Filtrar códigos válidos y eliminar duplicados
    codigos_validos = []
    for codigo in codigos:
        if es_codigo_cie10_valido(codigo):
            # Normalizar: quitar el punto si existe
            codigos_validos.append(codigo.replace('.', ''))
    
    return list(set(codigos_validos))

def es_codigo_cie10_valido(codigo):
    """Valida si un código CIE-10 es válido"""
    if not codigo or len(codigo) < 3:
        return False
    
    # Debe empezar con letra seguida de números
    if not re.match(r'^[A-Z]\d{2}', codigo):
        return False
    
    # Evitar códigos genéricos comunes en páginas web que no son diagnósticos
    codigos_genericos = ['G203', 'I134', 'H123', 'F999', 'Z999', 'X999']
    if codigo.replace('.', '') in codigos_genericos:
        return False
    
    return True

def calcular_similitud(codigo_colombia, codigos_orphanet):
    """Calcula similitud entre códigos"""
    if not codigos_orphanet:
        return 0.0
    
    max_similitud = 0.0
    codigo_colombia = codigo_colombia.upper().strip().replace('.', '')
    
    for codigo_orpha in codigos_orphanet:
        codigo_orpha = codigo_orpha.upper().strip().replace('.', '')
        
        if codigo_colombia == codigo_orpha:
            return 1.0  # Coincidencia exacta
        elif codigo_colombia[0] == codigo_orpha[0]:
            if len(codigo_colombia) >= 3 and len(codigo_orpha) >= 3:
                if codigo_colombia[:3] == codigo_orpha[:3]:
                    max_similitud = max(max_similitud, 0.8) # Coincidencia de categoría (3 dígitos)
                else:
                    max_similitud = max(max_similitud, 0.3) # Coincidencia de capítulo (letra)
    
    return max_similitud

if __name__ == "__main__":
    demonstrar_homologacion()
