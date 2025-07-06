#!/usr/bin/env python3
"""
PRUEBA DIRECTA ORPHANET - Basada en URL específica encontrada
URL ejemplo: https://www.orpha.net/es/disease/detail/932?name=Acondrog%C3%A9nesis&mode=name

Estrategia simplificada:
1. Usar URL directa de Orphanet en español
2. Probar tanto búsqueda por nombre como verificación directa
3. Implementar búsqueda inversa por código CIE-10
"""

import requests
import re
from urllib.parse import quote
import time

def probar_url_directa():
    """Prueba la URL específica que encontraste"""
    print("=" * 80)
    print("🎯 PRUEBA DIRECTA ORPHANET - URL ESPECÍFICA")
    print("=" * 80)
    
    # Caso específico que sabemos que existe
    caso_conocido = {
        "nombre": "Acondrogénesis",
        "codigo_colombia": "Q770",
        "orpha_number": "932",
        "url_conocida": "https://www.orpha.net/es/disease/detail/932?name=Acondrog%C3%A9nesis&mode=name"
    }
    
    print(f"📋 CASO DE PRUEBA: {caso_conocido['nombre']}")
    print(f"🔗 URL conocida: {caso_conocido['url_conocida']}")
    
    # Prueba 1: Acceso directo a URL conocida
    print(f"\n🔍 PRUEBA 1: Acceso directo a URL conocida")
    resultado_directo = acceder_url_directa(caso_conocido['url_conocida'])
    mostrar_resultado(resultado_directo, "URL directa")
    
    # Prueba 2: Construcción de URL de búsqueda
    print(f"\n🔍 PRUEBA 2: Búsqueda por nombre en español")
    resultado_busqueda = buscar_por_nombre_español(caso_conocido['nombre'])
    mostrar_resultado(resultado_busqueda, "Búsqueda español")
    
    # Prueba 3: Búsqueda por número ORPHA
    print(f"\n🔍 PRUEBA 3: Verificación por ORPHA:{caso_conocido['orpha_number']}")
    resultado_orpha = verificar_orpha_directo(caso_conocido['orpha_number'])
    mostrar_resultado(resultado_orpha, "ORPHA directo")
    
    # Prueba 4: Búsqueda inversa por código CIE-10
    print(f"\n🔍 PRUEBA 4: Búsqueda por código CIE-10: {caso_conocido['codigo_colombia']}")
    resultado_codigo = buscar_por_codigo_cie10(caso_conocido['codigo_colombia'])
    mostrar_resultado(resultado_codigo, "Por código CIE-10")
    
    print(f"\n{'='*80}")
    print("✅ PRUEBAS COMPLETADAS")
    print("Si alguna funciona, podemos aplicarla al resto del dataset")
    print("=" * 80)

def acceder_url_directa(url):
    """Accede directamente a una URL conocida"""
    try:
        headers = {"User-Agent": "OrphanetTest/1.0 (Research)"}
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            # Extraer información de la página
            return parsear_pagina_detalle(response.text, url)
        else:
            return {
                "exito": False,
                "error": f"HTTP {response.status_code}",
                "url": url
            }
            
    except Exception as e:
        return {
            "exito": False,
            "error": str(e),
            "url": url
        }

def buscar_por_nombre_español(nombre):
    """Busca usando el sistema de búsqueda en español"""
    try:
        # URL base de búsqueda
        base_url = "https://www.orpha.net/es/disease/search"
        
        # Parámetros de búsqueda
        params = {
            "query": nombre,
            "lang": "es"
        }
        
        headers = {"User-Agent": "OrphanetSearch/1.0"}
        response = requests.get(base_url, params=params, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            return parsear_resultados_busqueda(response.text, nombre)
        else:
            return {
                "exito": False,
                "error": f"HTTP {response.status_code}",
                "url": response.url
            }
            
    except Exception as e:
        return {
            "exito": False,
            "error": str(e),
            "nombre_buscado": nombre
        }

def verificar_orpha_directo(orpha_number):
    """Verifica acceso directo a página de ORPHA"""
    try:
        # URL directa al detalle
        url_detalle = f"https://www.orpha.net/es/disease/detail/{orpha_number}"
        
        headers = {"User-Agent": "OrphanetDirect/1.0"}
        response = requests.get(url_detalle, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            resultado = parsear_pagina_detalle(response.text, url_detalle)
            resultado["orpha_verificado"] = f"ORPHA:{orpha_number}"
            return resultado
        else:
            return {
                "exito": False,
                "error": f"HTTP {response.status_code}",
                "orpha": f"ORPHA:{orpha_number}",
                "url": url_detalle
            }
            
    except Exception as e:
        return {
            "exito": False,
            "error": str(e),
            "orpha": f"ORPHA:{orpha_number}"
        }

def buscar_por_codigo_cie10(codigo):
    """Búsqueda inversa: buscar enfermedades con código CIE-10 específico"""
    try:
        # Términos de búsqueda para código
        terminos = [
            f"CIE-10 {codigo}",
            f"ICD-10 {codigo}",
            codigo
        ]
        
        for termino in terminos:
            resultado = buscar_por_nombre_español(termino)
            if resultado.get("exito"):
                resultado["metodo_busqueda"] = f"Código: {termino}"
                return resultado
        
        return {
            "exito": False,
            "error": "No encontrado por código CIE-10",
            "codigo_buscado": codigo
        }
        
    except Exception as e:
        return {
            "exito": False,
            "error": str(e),
            "codigo_buscado": codigo
        }

def parsear_pagina_detalle(html_content, url):
    """Parsea página de detalle de enfermedad"""
    resultado = {
        "exito": True,
        "url": url,
        "nombres": [],
        "codigos_orpha": [],
        "codigos_cie10": [],
        "sinonimos": [],
        "contenido_encontrado": True
    }
    
    try:
        # Buscar números ORPHA
        orpha_matches = re.findall(r'ORPHA[:\s]*(\d+)', html_content, re.IGNORECASE)
        resultado["codigos_orpha"] = [f"ORPHA:{num}" for num in set(orpha_matches)]
        
        # Buscar códigos CIE-10 con diferentes patrones
        cie10_patterns = [
            r'CIE-?10[:\s]*([A-Z]\d{2}\.?\d{0,2})',
            r'ICD-?10[:\s]*([A-Z]\d{2}\.?\d{0,2})',
            r'\b([A-Z]\d{2}\.?\d{0,2})\b'
        ]
        
        todos_cie10 = []
        for pattern in cie10_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            todos_cie10.extend(matches)
        
        # Filtrar códigos CIE-10 válidos
        resultado["codigos_cie10"] = list(set([c for c in todos_cie10 if es_codigo_cie10_valido(c)]))
        
        # Buscar título/nombre de la enfermedad
        title_patterns = [
            r'<title>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'<h2[^>]*>([^<]+)</h2>'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                resultado["nombres"].extend([m.strip() for m in matches])
                break
        
        # Verificar si hay contenido real de enfermedad
        indicadores_contenido = [
            'orpha', 'enfermedad', 'síndrome', 'trastorno', 
            'prevalencia', 'síntomas', 'genes'
        ]
        
        contenido_lower = html_content.lower()
        hay_contenido = any(ind in contenido_lower for ind in indicadores_contenido)
        resultado["contenido_encontrado"] = hay_contenido
        
        if not hay_contenido:
            resultado["exito"] = False
            resultado["error"] = "Página sin contenido específico de enfermedad"
        
    except Exception as e:
        resultado["error"] = str(e)
        resultado["exito"] = False
    
    return resultado

def parsear_resultados_busqueda(html_content, termino_busqueda):
    """Parsea resultados de búsqueda"""
    resultado = {
        "exito": False,
        "termino_busqueda": termino_busqueda,
        "enfermedades_encontradas": [],
        "codigos_orpha": [],
        "codigos_cie10": [],
        "links_detalle": []
    }
    
    try:
        # Buscar links a páginas de detalle
        detail_links = re.findall(r'/disease/detail/(\d+)', html_content)
        resultado["links_detalle"] = list(set(detail_links))
        
        # Buscar códigos ORPHA
        orpha_matches = re.findall(r'ORPHA[:\s]*(\d+)', html_content, re.IGNORECASE)
        resultado["codigos_orpha"] = [f"ORPHA:{num}" for num in set(orpha_matches)]
        
        # Buscar códigos CIE-10
        cie10_matches = re.findall(r'\b([A-Z]\d{2}\.?\d{0,2})\b', html_content)
        resultado["codigos_cie10"] = list(set([c for c in cie10_matches if es_codigo_cie10_valido(c)]))
        
        if detail_links or orpha_matches or resultado["codigos_cie10"]:
            resultado["exito"] = True
        
    except Exception as e:
        resultado["error"] = str(e)
    
    return resultado

def es_codigo_cie10_valido(codigo):
    """Valida si es un código CIE-10 real"""
    if not codigo or len(codigo) < 3:
        return False
    
    # Debe empezar con letra seguida de números
    if not re.match(r'^[A-Z]\d{2}', codigo):
        return False
    
    # Evitar códigos que son claramente de navegación web
    codigos_web = ['G203', 'I134', 'H123', 'F999', 'Z999', 'X999', 'A404']
    if codigo in codigos_web:
        return False
    
    return True

def mostrar_resultado(resultado, metodo):
    """Muestra resultado de forma clara"""
    if resultado.get("exito"):
        print(f"   ✅ {metodo}: ÉXITO")
        
        if resultado.get("codigos_orpha"):
            print(f"      🏷️  ORPHA: {', '.join(resultado['codigos_orpha'])}")
        
        if resultado.get("codigos_cie10"):
            print(f"      🔢 CIE-10: {', '.join(resultado['codigos_cie10'])}")
        
        if resultado.get("nombres"):
            print(f"      📝 Nombres: {', '.join(resultado['nombres'][:2])}")
        
        if resultado.get("links_detalle"):
            print(f"      🔗 Links detalle: {len(resultado['links_detalle'])} encontrados")
            
        if resultado.get("url"):
            print(f"      🌐 URL: {resultado['url']}")
    else:
        print(f"   ❌ {metodo}: FALLO")
        if resultado.get("error"):
            print(f"      Error: {resultado['error']}")
        if resultado.get("url"):
            print(f"      URL intentada: {resultado['url']}")

if __name__ == "__main__":
    probar_url_directa()
