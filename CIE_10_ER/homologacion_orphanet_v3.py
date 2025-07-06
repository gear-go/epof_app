#!/usr/bin/env python3
"""
HOMOLOGACIÓN ORPHANET MEJORADA v3.0
Versión multiidioma y búsqueda híbrida

Mejoras implementadas:
1. Búsqueda en español e inglés
2. Búsqueda por código CIE-10 (proceso inverso)
3. Uso de URLs directas de Orphanet
4. Múltiples estrategias de búsqueda

Basado en hallazgo: Acondrogénesis existe en:
https://www.orpha.net/es/disease/detail/932?name=Acondrog%C3%A9nesis&mode=name
"""

import pandas as pd
import requests
import time
from datetime import datetime
import re
from urllib.parse import quote, unquote
import json

# Configuración mejorada
ORPHANET_URLS = {
    "search_es": "https://www.orpha.net/es/disease/search",
    "search_en": "https://www.orpha.net/en/disease/search", 
    "detail_es": "https://www.orpha.net/es/disease/detail",
    "detail_en": "https://www.orpha.net/en/disease/detail"
}

USER_AGENT = "OrphanetHomologation/3.0 (Research/Colombia)"
DELAY = 1.5

class OrphanetHomologatorV3:
    """Homologador mejorado con búsqueda multiidioma"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.resultados = []
        
    def demostrar_busqueda_hibrida(self):
        """Demuestra múltiples estrategias de búsqueda"""
        print("=" * 80)
        print("🔍 HOMOLOGACIÓN ORPHANET v3.0 - BÚSQUEDA HÍBRIDA")
        print("=" * 80)
        print("Estrategias: Español + Inglés + Búsqueda por código CIE-10")
        print("=" * 80)
        
        # Casos de prueba específicos
        casos_prueba = [
            {
                "nombre_es": "Acondrogénesis",
                "nombre_en": "Achondrogenesis", 
                "codigo_cie10": "Q770",
                "orpha_esperado": "932"  # Del URL que encontraste
            },
            {
                "nombre_es": "Acondroplasia",
                "nombre_en": "Achondroplasia",
                "codigo_cie10": "Q774",
                "orpha_esperado": None
            },
            {
                "nombre_es": "Acromegalia", 
                "nombre_en": "Acromegaly",
                "codigo_cie10": "E220",
                "orpha_esperado": None
            }
        ]
        
        for i, caso in enumerate(casos_prueba):
            print(f"\n{'='*15} CASO {i+1}: {caso['nombre_es']} {'='*15}")
            self.procesar_caso_completo(caso)
            time.sleep(DELAY)
        
        print(f"\n{'='*80}")
        print("✅ DEMOSTRACIÓN HÍBRIDA COMPLETADA")
        print("Se probaron múltiples estrategias de búsqueda")
        print("=" * 80)
    
    def procesar_caso_completo(self, caso):
        """Procesa un caso con todas las estrategias"""
        print(f"📋 DATOS ORIGINALES:")
        print(f"   Español: {caso['nombre_es']}")
        print(f"   Inglés: {caso['nombre_en']}")
        print(f"   CIE-10: {caso['codigo_cie10']}")
        
        resultados = {}
        
        # Estrategia 1: Búsqueda directa en español
        print(f"\n🔍 ESTRATEGIA 1: Búsqueda en español")
        resultado_es = self.buscar_por_nombre(caso['nombre_es'], idioma='es')
        resultados['español'] = resultado_es
        self.mostrar_resultado(resultado_es, "Español")
        
        # Estrategia 2: Búsqueda en inglés
        print(f"\n🔍 ESTRATEGIA 2: Búsqueda en inglés")
        resultado_en = self.buscar_por_nombre(caso['nombre_en'], idioma='en')
        resultados['inglés'] = resultado_en
        self.mostrar_resultado(resultado_en, "Inglés")
        
        # Estrategia 3: Búsqueda por código CIE-10 (proceso inverso)
        print(f"\n🔍 ESTRATEGIA 3: Búsqueda por código CIE-10")
        resultado_codigo = self.buscar_por_codigo_cie10(caso['codigo_cie10'])
        resultados['por_codigo'] = resultado_codigo
        self.mostrar_resultado(resultado_codigo, "Por código CIE-10")
        
        # Estrategia 4: Verificación directa si tenemos ORPHA conocido
        if caso.get('orpha_esperado'):
            print(f"\n🔍 ESTRATEGIA 4: Verificación directa ORPHA:{caso['orpha_esperado']}")
            resultado_directo = self.verificar_orpha_directo(caso['orpha_esperado'])
            resultados['directo'] = resultado_directo
            self.mostrar_resultado(resultado_directo, "Verificación directa")
        
        # Análisis consolidado
        self.analizar_resultados_consolidados(caso, resultados)
    
    def buscar_por_nombre(self, nombre, idioma='es'):
        """Busca por nombre en idioma específico"""
        try:
            # URL de búsqueda según idioma
            search_url = ORPHANET_URLS[f"search_{idioma}"]
            
            # Parámetros de búsqueda
            params = {
                'query': nombre,
                'mode': 'name'
            }
            
            response = self.session.get(search_url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                return self.parsear_resultados_busqueda(response.text, nombre, idioma)
            else:
                return {
                    "exito": False,
                    "error": f"HTTP {response.status_code}",
                    "url": response.url
                }
                
        except Exception as e:
            search_url = ORPHANET_URLS.get(f"search_{idioma}", "https://www.orpha.net/es/disease/search")
            return {
                "exito": False,
                "error": str(e),
                "url": f"{search_url}?query={quote(nombre)}"
            }
    
    def buscar_por_codigo_cie10(self, codigo):
        """Búsqueda inversa: dado código CIE-10, buscar enfermedad"""
        try:
            # Buscar páginas que contengan el código
            search_terms = [
                f"ICD-10 {codigo}",
                f"CIE-10 {codigo}",
                codigo
            ]
            
            for term in search_terms:
                resultado = self.buscar_por_nombre(term, idioma='es')
                if resultado.get('exito'):
                    resultado['metodo_busqueda'] = f"Por código: {term}"
                    return resultado
            
            return {
                "exito": False,
                "error": "No encontrado por código CIE-10",
                "metodo_busqueda": "Por código CIE-10"
            }
            
        except Exception as e:
            return {
                "exito": False,
                "error": str(e),
                "metodo_busqueda": "Por código CIE-10"
            }
    
    def verificar_orpha_directo(self, orpha_number):
        """Verifica directamente un número ORPHA conocido"""
        try:
            # URL directa al detalle
            detail_url = f"{ORPHANET_URLS['detail_es']}/{orpha_number}"
            
            response = self.session.get(detail_url, timeout=10, verify=False)
            
            if response.status_code == 200:
                return self.parsear_detalle_enfermedad(response.text, orpha_number)
            else:
                return {
                    "exito": False,
                    "error": f"HTTP {response.status_code}",
                    "url": detail_url
                }
                
        except Exception as e:
            return {
                "exito": False,
                "error": str(e),
                "orpha": f"ORPHA:{orpha_number}"
            }
    
    def parsear_resultados_busqueda(self, html_content, termino_busqueda, idioma):
        """Parsea resultados de búsqueda"""
        resultado = {
            "exito": False,
            "termino_busqueda": termino_busqueda,
            "idioma": idioma,
            "enfermedades_encontradas": [],
            "codigos_orpha": [],
            "codigos_cie10": []
        }
        
        try:
            # Buscar números ORPHA
            orpha_matches = re.findall(r'ORPHA[:\s]*(\d+)', html_content, re.IGNORECASE)
            resultado["codigos_orpha"] = [f"ORPHA:{num}" for num in set(orpha_matches)]
            
            # Buscar códigos CIE-10
            cie10_matches = re.findall(r'\b([A-Z]\d{2}\.?\d{0,2})\b', html_content)
            resultado["codigos_cie10"] = list(set([c for c in cie10_matches if self.es_codigo_cie10_valido(c)]))
            
            # Buscar links a detalles de enfermedades
            detail_links = re.findall(r'/disease/detail/(\d+)', html_content)
            
            if orpha_matches or detail_links or resultado["codigos_cie10"]:
                resultado["exito"] = True
                resultado["detalles_encontrados"] = list(set(detail_links))
            
        except Exception as e:
            resultado["error"] = str(e)
        
        return resultado
    
    def parsear_detalle_enfermedad(self, html_content, orpha_number):
        """Parsea página de detalle de enfermedad"""
        resultado = {
            "exito": True,
            "orpha": f"ORPHA:{orpha_number}",
            "nombres": [],
            "sinonimos": [],
            "codigos_cie10": [],
            "descripcion": ""
        }
        
        try:
            # Extraer nombre principal
            nombre_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
            if nombre_matches:
                resultado["nombres"] = [nombre_matches[0].strip()]
            
            # Extraer códigos CIE-10
            cie10_matches = re.findall(r'ICD-?10[:\s]*([A-Z]\d{2}\.?\d{0,2})', html_content, re.IGNORECASE)
            resultado["codigos_cie10"] = list(set([c for c in cie10_matches if self.es_codigo_cie10_valido(c)]))
            
            # Extraer sinónimos si están disponibles
            sinonimo_matches = re.findall(r'Synonym[s]?[:\s]*([^<\n]+)', html_content, re.IGNORECASE)
            resultado["sinonimos"] = [s.strip() for s in sinonimo_matches if s.strip()]
            
        except Exception as e:
            resultado["error"] = str(e)
        
        return resultado
    
    def es_codigo_cie10_valido(self, codigo):
        """Valida código CIE-10"""
        if not codigo or len(codigo) < 3:
            return False
        return re.match(r'^[A-Z]\d{2}', codigo) is not None
    
    def mostrar_resultado(self, resultado, estrategia):
        """Muestra resultado de una estrategia"""
        if resultado.get('exito'):
            print(f"   ✅ {estrategia}: ENCONTRADA")
            
            if resultado.get('codigos_orpha'):
                print(f"      🏷️  ORPHA: {', '.join(resultado['codigos_orpha'])}")
            
            if resultado.get('codigos_cie10'):
                print(f"      🔢 CIE-10: {', '.join(resultado['codigos_cie10'])}")
            
            if resultado.get('nombres'):
                print(f"      📝 Nombres: {', '.join(resultado['nombres'])}")
                
        else:
            print(f"   ❌ {estrategia}: No encontrada")
            if resultado.get('error'):
                print(f"      Error: {resultado['error']}")
    
    def analizar_resultados_consolidados(self, caso, resultados):
        """Analiza todos los resultados consolidados"""
        print(f"\n📊 ANÁLISIS CONSOLIDADO:")
        
        # Recopilar todos los códigos encontrados
        todos_orpha = []
        todos_cie10 = []
        
        for estrategia, resultado in resultados.items():
            if resultado.get('exito'):
                todos_orpha.extend(resultado.get('codigos_orpha', []))
                todos_cie10.extend(resultado.get('codigos_cie10', []))
        
        todos_orpha = list(set(todos_orpha))
        todos_cie10 = list(set(todos_cie10))
        
        if todos_orpha or todos_cie10:
            print(f"   ✅ ENFERMEDAD ENCONTRADA EN ORPHANET")
            if todos_orpha:
                print(f"   🏷️  Códigos ORPHA consolidados: {', '.join(todos_orpha)}")
            if todos_cie10:
                print(f"   🔢 Códigos CIE-10 Orphanet: {', '.join(todos_cie10)}")
            
            # Comparar con código Colombia
            codigo_colombia = caso['codigo_cie10']
            if codigo_colombia in todos_cie10:
                print(f"   🎯 COINCIDENCIA EXACTA: {codigo_colombia}")
            else:
                similitud = self.calcular_similitud_maxima(codigo_colombia, todos_cie10)
                print(f"   ⚖️  Similitud máxima: {similitud*100:.1f}%")
                print(f"   📋 Colombia: {codigo_colombia} vs Orphanet: {todos_cie10}")
        else:
            print(f"   ❌ NO ENCONTRADA EN NINGUNA ESTRATEGIA")
    
    def calcular_similitud_maxima(self, codigo_colombia, codigos_orphanet):
        """Calcula similitud máxima"""
        if not codigos_orphanet:
            return 0.0
        
        max_sim = 0.0
        for codigo in codigos_orphanet:
            if codigo_colombia == codigo:
                return 1.0
            elif codigo_colombia[0] == codigo[0]:
                if len(codigo_colombia) >= 3 and len(codigo) >= 3:
                    if codigo_colombia[:3] == codigo[:3]:
                        max_sim = max(max_sim, 0.8)
                    else:
                        max_sim = max(max_sim, 0.3)
        
        return max_sim

def main():
    """Función principal mejorada"""
    print("🚀 Iniciando homologación híbrida con Orphanet")
    
    homologator = OrphanetHomologatorV3()
    homologator.demostrar_busqueda_hibrida()

if __name__ == "__main__":
    main()
