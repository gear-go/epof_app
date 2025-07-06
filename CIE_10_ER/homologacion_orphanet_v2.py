#!/usr/bin/env python3
"""
Script mejorado para Homologación de Códigos con Orphanet
Versión 2.0 - Búsqueda específica y parsing mejorado

Funcionalidades mejoradas:
1. Búsqueda más específica en Orphanet
2. Parsing mejorado de resultados HTML
3. Validación de códigos encontrados
4. Análisis estadístico detallado

Autor: Análisis GRD Enfermedades Raras Colombia
Fecha: Julio 2025
"""

import pandas as pd
import requests
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import json
import warnings
warnings.filterwarnings("ignore")

# Configuración mejorada
ORPHANET_BASE_URL = "https://www.orpha.net/consor/cgi-bin"
DELAY_BETWEEN_REQUESTS = 1.5  # Reducir delay para eficiencia
MAX_RETRIES = 2
TIMEOUT = 8
USER_AGENT = "OrphanetHomologation/2.0 (Research/Colombia)"

class OrphanetHomologatorV2:
    """Clase mejorada para homologación con Orphanet"""
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.total_requests = 0
        
    def load_dataset(self):
        """Carga el dataset de enfermedades raras de Colombia"""
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            print(f"✅ Dataset cargado: {len(self.df)} enfermedades")
            return True
        except Exception as e:
            print(f"❌ Error al cargar dataset: {e}")
            return False
    
    def normalize_disease_name(self, name):
        """Normaliza el nombre de la enfermedad para búsqueda más efectiva"""
        if pd.isna(name):
            return ""
        
        name = str(name).strip()
        
        # Remover palabras comunes al inicio
        prefixes_to_remove = [
            'sindrome de ', 'síndrome de ', 'syndrome ', 
            'enfermedad de ', 'disease ', 'trastorno de ', 'disorder '
        ]
        
        name_lower = name.lower()
        for prefix in prefixes_to_remove:
            if name_lower.startswith(prefix):
                name = name[len(prefix):].strip()
                break
        
        # Limpiar caracteres especiales
        name = re.sub(r'[^\w\s\-\']', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Tomar las primeras palabras más significativas
        words = name.split()
        if len(words) > 4:
            name = ' '.join(words[:4])
        
        return name.title()
    
    def search_orphanet_disease(self, disease_name):
        """Realiza búsqueda específica en Orphanet"""
        normalized_name = self.normalize_disease_name(disease_name)
        if not normalized_name:
            return {"success": False, "error": "Nombre vacío"}
        
        # Múltiples estrategias de búsqueda
        search_strategies = [
            normalized_name,
            normalized_name.split()[0],  # Primera palabra
            ' '.join(normalized_name.split()[:2])  # Primeras dos palabras
        ]
        
        best_result = {"success": False, "matches": 0}
        
        for search_term in search_strategies:
            if len(search_term) < 3:
                continue
                
            result = self.perform_orphanet_search(search_term, disease_name)
            
            if result["success"] and result.get("matches", 0) > best_result.get("matches", 0):
                best_result = result
                
            # Si encontramos códigos Orphá específicos, usar ese resultado
            if result.get("orpha_codes") and len(result["orpha_codes"]) > 0:
                return result
            
            time.sleep(0.5)  # Pequeña pausa entre estrategias
        
        return best_result
    
    def perform_orphanet_search(self, search_term, original_name):
        """Ejecuta la búsqueda en Orphanet"""
        search_url = f"{ORPHANET_BASE_URL}/Disease_Search.php"
        
        params = {
            "lng": "EN",
            "data_id": "Pat",
            "search": "Disease_Search_Simple", 
            "Typ": "Pat",
            "diseaseGroup": search_term
        }
        
        self.total_requests += 1
        
        try:
            response = self.session.get(
                search_url,
                params=params,
                timeout=TIMEOUT,
                verify=False
            )
            
            if response.status_code == 200:
                return self.parse_search_results(response.text, search_term, original_name)
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_search_results(self, html_content, search_term, original_name):
        """Parsea resultados HTML con BeautifulSoup para mayor precisión"""
        result = {
            "success": False,
            "original_name": original_name,
            "search_term": search_term,
            "orpha_codes": [],
            "icd10_codes": [],
            "disease_names": [],
            "matches": 0
        }
        
        try:
            # Usar BeautifulSoup para parsing más robusto
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar códigos ORPHA específicos
            orpha_pattern = r'ORPHA:(\d+)'
            orpha_matches = re.findall(orpha_pattern, html_content, re.IGNORECASE)
            
            # Buscar códigos ICD-10 válidos (evitar códigos genéricos)
            icd10_pattern = r'\b([A-Z]\d{2}\.?\d{0,2})\b'
            potential_icd10 = re.findall(icd10_pattern, html_content)
            
            # Filtrar códigos ICD-10 válidos (evitar códigos como G203, I134 que parecen genéricos)
            valid_icd10 = []
            for code in potential_icd10:
                if self.is_valid_icd10_code(code):
                    valid_icd10.append(code)
            
            # Buscar nombres de enfermedades en links o títulos
            disease_links = soup.find_all('a', href=True)
            for link in disease_links:
                if 'disease' in link.get('href', '').lower():
                    disease_names = link.get_text().strip()
                    if disease_names and len(disease_names) > 5:
                        result["disease_names"].append(disease_names)
            
            # Evaluar calidad de los resultados
            result["orpha_codes"] = [f"ORPHA:{code}" for code in set(orpha_matches)]
            result["icd10_codes"] = list(set(valid_icd10))
            result["matches"] = len(orpha_matches) + len(valid_icd10)
            
            # Determinar si la búsqueda fue exitosa
            if orpha_matches or valid_icd10:
                result["success"] = True
                print(f"✅ '{search_term}': {len(orpha_matches)} Orphá, {len(valid_icd10)} ICD-10 válidos")
            else:
                print(f"⚠️ '{search_term}': Sin resultados específicos")
            
        except Exception as e:
            print(f"❌ Error parseando '{search_term}': {e}")
            # Fallback a regex simple
            orpha_matches = re.findall(r'ORPHA:(\d+)', html_content, re.IGNORECASE)
            if orpha_matches:
                result["orpha_codes"] = [f"ORPHA:{code}" for code in set(orpha_matches)]
                result["success"] = True
                result["matches"] = len(orpha_matches)
        
        return result
    
    def is_valid_icd10_code(self, code):
        """Valida si un código ICD-10 es válido y específico"""
        if not code or len(code) < 3:
            return False
        
        # Códigos ICD-10 válidos empiezan con letra seguida de números
        if not re.match(r'^[A-Z]\d{2}', code):
            return False
        
        # Evitar códigos que parecen genéricos o de navegación web
        generic_codes = ['G203', 'I134', 'H123', 'F999', 'Z999']
        if code in generic_codes:
            return False
        
        # Validar longitud apropiada
        if len(code) > 6:
            return False
            
        return True
    
    def calculate_code_similarity(self, colombia_code, orphanet_codes):
        """Calcula similitud entre códigos con lógica mejorada"""
        if not orphanet_codes:
            return 0.0
        
        colombia_code = str(colombia_code).upper().strip()
        max_similarity = 0.0
        
        for orpha_code in orphanet_codes:
            orpha_code = str(orpha_code).upper().strip()
            
            # Coincidencia exacta
            if colombia_code == orpha_code:
                return 1.0
            
            # Misma categoría principal (primera letra)
            if colombia_code[0] == orpha_code[0]:
                similarity = 0.3
                
                # Misma subcategoría (primeros 3 caracteres)
                if len(colombia_code) >= 3 and len(orpha_code) >= 3:
                    if colombia_code[:3] == orpha_code[:3]:
                        similarity = 0.7
                        
                        # Código muy similar (4+ caracteres)
                        if len(colombia_code) >= 4 and len(orpha_code) >= 4:
                            if colombia_code[:4] == orpha_code[:4]:
                                similarity = 0.9
                
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def process_homologation(self, sample_size=15):
        """Procesa homologación con lógica mejorada"""
        if self.df is None:
            return False
        
        sample_df = self.df.head(sample_size).copy()
        
        print(f"\n🔍 HOMOLOGACIÓN ORPHANET v2.0 - {len(sample_df)} ENFERMEDADES")
        print("=" * 70)
        
        results = []
        successful_searches = 0
        orpha_codes_found = 0
        icd10_matches = 0
        
        for i, (idx, row) in enumerate(sample_df.iterrows()):
            disease_name = row['Nombre_Enfermedad'][:50]
            print(f"\n[{i + 1}/{len(sample_df)}] {disease_name}...")
            
            # Búsqueda en Orphanet
            search_result = self.search_orphanet_disease(row['Nombre_Enfermedad'])
            
            # Análisis de resultados
            homolog_result = {
                "numero": row['Número'],
                "nombre_original": row['Nombre_Enfermedad'],
                "codigo_cie10_colombia": row['Código_CIE10'],
                "observaciones": row.get('Observaciones', ''),
                "search_result": search_result,
                "timestamp": datetime.now().isoformat()
            }
            
            if search_result["success"]:
                successful_searches += 1
                homolog_result["status"] = "ENCONTRADA"
                
                # Contabilizar códigos Orphá
                if search_result.get("orpha_codes"):
                    orpha_codes_found += 1
                
                # Analizar coincidencias ICD-10
                colombia_code = str(row['Código_CIE10']).strip()
                orphanet_icd10 = search_result.get("icd10_codes", [])
                
                homolog_result["icd10_exact_match"] = colombia_code in orphanet_icd10
                homolog_result["icd10_similarity"] = self.calculate_code_similarity(colombia_code, orphanet_icd10)
                
                if homolog_result["icd10_exact_match"]:
                    icd10_matches += 1
                    
            else:
                homolog_result["status"] = "NO_ENCONTRADA"
                homolog_result["icd10_exact_match"] = False
                homolog_result["icd10_similarity"] = 0.0
            
            results.append(homolog_result)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        self.results = results
        
        # Estadísticas finales
        print(f"\n📊 ESTADÍSTICAS FINALES")
        print("=" * 70)
        print(f"🔍 Total procesado: {len(results)}")
        print(f"✅ Búsquedas exitosas: {successful_searches} ({successful_searches/len(results)*100:.1f}%)")
        print(f"🏷️  Con códigos Orphá: {orpha_codes_found} ({orpha_codes_found/len(results)*100:.1f}%)")
        print(f"🎯 Coincidencias ICD-10: {icd10_matches} ({icd10_matches/len(results)*100:.1f}%)")
        print(f"🌐 Total requests HTTP: {self.total_requests}")
        
        return True
    
    def generate_enhanced_report(self):
        """Genera reporte mejorado"""
        if not self.results:
            return None
        
        # Preparar datos para el reporte
        report_data = []
        
        for result in self.results:
            search_info = result.get("search_result", {})
            
            row = {
                "Número": result["numero"],
                "Nombre_Enfermedad": result["nombre_original"],
                "CIE10_Colombia": result["codigo_cie10_colombia"],
                "Estado_Búsqueda": result.get("status", "DESCONOCIDO"),
                "Término_Búsqueda": search_info.get("search_term", ""),
                "Códigos_Orphá": "; ".join(search_info.get("orpha_codes", [])),
                "CIE10_Orphanet": "; ".join(search_info.get("icd10_codes", [])),
                "Coincidencia_Exacta": result.get("icd10_exact_match", False),
                "Similitud_CIE10": result.get("icd10_similarity", 0.0),
                "Nombres_Encontrados": "; ".join(search_info.get("disease_names", [])[:2]),
                "Observaciones": result["observaciones"]
            }
            report_data.append(row)
        
        # Crear DataFrame y guardar
        report_df = pd.DataFrame(report_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"homologacion_orphanet_v2_{timestamp}.csv"
        
        report_df.to_csv(filename, index=False, encoding='utf-8')
        
        # Estadísticas del reporte
        total = len(report_df)
        found = len(report_df[report_df["Estado_Búsqueda"] == "ENCONTRADA"])
        with_orpha = len(report_df[report_df["Códigos_Orphá"] != ""])
        exact_matches = len(report_df[report_df["Coincidencia_Exacta"] == True])
        high_similarity = len(report_df[report_df["Similitud_CIE10"] >= 0.7])
        
        print(f"\n📋 REPORTE GENERADO: {filename}")
        print("-" * 50)
        print(f"📊 Total procesado: {total}")
        print(f"✅ Encontradas: {found} ({found/total*100:.1f}%)")
        print(f"🏷️  Con códigos Orphá: {with_orpha} ({with_orpha/total*100:.1f}%)")
        print(f"🎯 Coincidencias exactas: {exact_matches} ({exact_matches/total*100:.1f}%)")
        print(f"⭐ Alta similitud: {high_similarity} ({high_similarity/total*100:.1f}%)")
        
        return filename

def main():
    """Función principal mejorada"""
    print("=" * 80)
    print("🔍 HOMOLOGACIÓN ORPHANET v2.0 - COLOMBIA")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Verificar si BeautifulSoup está disponible
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup disponible para parsing HTML")
    except ImportError:
        print("⚠️ BeautifulSoup no disponible, usando regex básico")
    
    csv_path = "enfermedades_raras_colombia_2023_corregido.csv"
    
    try:
        homologator = OrphanetHomologatorV2(csv_path)
        
        if not homologator.load_dataset():
            return
        
        # Procesar muestra
        sample_size = 10  # Muestra reducida para prueba inicial
        print(f"\n🎯 Procesando muestra de {sample_size} enfermedades")
        print(f"⏱️ Tiempo estimado: {sample_size * DELAY_BETWEEN_REQUESTS / 60:.1f} minutos")
        
        if homologator.process_homologation(sample_size):
            homologator.generate_enhanced_report()
            print(f"\n🎉 HOMOLOGACIÓN COMPLETADA")
        else:
            print("❌ Error en homologación")
            
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
