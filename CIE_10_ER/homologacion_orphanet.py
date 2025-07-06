#!/usr/bin/env python3
"""
Script para Homologación de Códigos CIE-10 con Orphanet
Basado en validación exitosa de conectividad (70.6% éxito)

Funcionalidades:
1. Búsqueda de enfermedades en Orphanet
2. Obtención de códigos Orphá
3. Validación cruzada con códigos CIE-10
4. Generación de mapping Colombia-Orphanet

Autor: Análisis GRD Enfermedades Raras Colombia
Fecha: Julio 2025
"""

import pandas as pd
import requests
import time
import re
from datetime import datetime
import json
from urllib.parse import urlencode, quote
import warnings
warnings.filterwarnings("ignore")

# Configuración
ORPHANET_SEARCH_URL = "https://www.orpha.net/consor/cgi-bin/Disease_Search.php"
DELAY_BETWEEN_REQUESTS = 2  # segundos
MAX_RETRIES = 3
TIMEOUT = 10
USER_AGENT = "OrphanetHomologation/1.0 (Research/Colombia)"

class OrphanetHomologator:
    """Clase para homologación de códigos con Orphanet"""
    
    def __init__(self, csv_path):
        """Inicializa con el dataset de enfermedades raras de Colombia"""
        self.csv_path = csv_path
        self.df = None
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
    def load_dataset(self):
        """Carga el dataset de enfermedades raras de Colombia"""
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            print(f"✅ Dataset cargado: {len(self.df)} enfermedades")
            print(f"📊 Columnas: {list(self.df.columns)}")
            return True
        except Exception as e:
            print(f"❌ Error al cargar dataset: {e}")
            return False
    
    def clean_disease_name(self, name):
        """Limpia el nombre de la enfermedad para búsqueda"""
        if pd.isna(name):
            return ""
        
        # Remover caracteres especiales y normalizar
        name = str(name).strip()
        name = re.sub(r'\s+', ' ', name)  # Espacios múltiples
        name = re.sub(r'[^\w\s\-\']', ' ', name)  # Solo letras, números, guiones y apostrofes
        name = name.title()  # Primera letra mayúscula
        
        # Remover palabras comunes que pueden interferir
        stop_words = ['sindrome', 'syndrome', 'enfermedad', 'disease', 'trastorno', 'disorder']
        words = name.split()
        words = [w for w in words if w.lower() not in stop_words]
        
        return ' '.join(words)[:50]  # Limitar longitud
    
    def search_orphanet(self, disease_name, max_results=5):
        """Busca una enfermedad en Orphanet"""
        clean_name = self.clean_disease_name(disease_name)
        if not clean_name:
            return {"success": False, "error": "Nombre vacío"}
        
        # Parámetros de búsqueda
        params = {
            "lng": "EN",
            "data_id": "Pat",
            "search": "Disease_Search_Simple",
            "Typ": "Pat",
            "diseaseGroup": clean_name
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    ORPHANET_SEARCH_URL, 
                    params=params, 
                    timeout=TIMEOUT,
                    verify=False
                )
                
                if response.status_code == 200:
                    return self.parse_orphanet_results(response.text, disease_name, clean_name)
                else:
                    print(f"⚠️ HTTP {response.status_code} para '{clean_name}' (intento {attempt + 1})")
                    
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1} para '{clean_name}': {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 1))
        
        return {"success": False, "error": "Máximo de reintentos alcanzado"}
    
    def parse_orphanet_results(self, html_content, original_name, search_term):
        """Parsea los resultados HTML de Orphanet"""
        results = {
            "success": True,
            "original_name": original_name,
            "search_term": search_term,
            "matches": [],
            "orpha_codes": [],
            "icd10_codes": []
        }
        
        # Buscar patrones típicos en el HTML de Orphanet
        orpha_pattern = r'ORPHA:(\d+)'
        orpha_matches = re.findall(orpha_pattern, html_content)
        
        # Buscar códigos ICD-10 en los resultados
        icd10_pattern = r'([A-Z]\d{2}\.?\d*)'
        icd10_matches = re.findall(icd10_pattern, html_content)
        
        # Buscar nombres de enfermedades
        disease_pattern = r'<b>([^<]+)</b>'
        disease_matches = re.findall(disease_pattern, html_content)
        
        # Procesar códigos Orphá encontrados
        for orpha_code in set(orpha_matches):
            results["orpha_codes"].append(f"ORPHA:{orpha_code}")
        
        # Procesar códigos ICD-10 encontrados
        for icd_code in set(icd10_matches):
            if len(icd_code) >= 3:  # Códigos ICD-10 válidos
                results["icd10_codes"].append(icd_code)
        
        # Determinar si hay coincidencias útiles
        has_results = len(orpha_matches) > 0 or len(icd10_matches) > 0
        
        if has_results:
            results["matches"] = disease_matches[:3]  # Primeros 3 matches
            print(f"✅ '{search_term}': {len(orpha_matches)} códigos Orphá, {len(icd10_matches)} códigos ICD-10")
        else:
            print(f"⚠️ '{search_term}': Sin resultados específicos")
            results["success"] = False
        
        return results
    
    def process_sample(self, sample_size=50):
        """Procesa una muestra del dataset para homologación"""
        if self.df is None:
            print("❌ Dataset no cargado")
            return False
        
        # Tomar muestra representativa
        sample_df = self.df.head(sample_size).copy()
        
        print(f"\n🔍 INICIANDO HOMOLOGACIÓN DE {len(sample_df)} ENFERMEDADES")
        print("=" * 70)
        
        results = []
        successful_matches = 0
        
        for i, (idx, row) in enumerate(sample_df.iterrows()):
            print(f"\n[{i + 1}/{len(sample_df)}] Procesando: {row['Nombre_Enfermedad'][:60]}...")
            
            # Buscar en Orphanet
            search_result = self.search_orphanet(row['Nombre_Enfermedad'])
            
            # Agregar información del dataset original
            homolog_result = {
                "numero": row['Número'],
                "nombre_original": row['Nombre_Enfermedad'],
                "codigo_cie10_colombia": row['Código_CIE10'],
                "observaciones": row.get('Observaciones', ''),
                "orphanet_search": search_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Análisis de coincidencias
            if search_result["success"]:
                successful_matches += 1
                homolog_result["homologation_status"] = "FOUND"
                
                # Comparar códigos ICD-10
                colombia_code = str(row['Código_CIE10']).strip()
                orphanet_codes = search_result.get("icd10_codes", [])
                
                homolog_result["icd10_match"] = colombia_code in orphanet_codes
                homolog_result["icd10_similarity"] = self.calculate_icd10_similarity(colombia_code, orphanet_codes)
                
            else:
                homolog_result["homologation_status"] = "NOT_FOUND"
                homolog_result["icd10_match"] = False
                homolog_result["icd10_similarity"] = 0.0
            
            results.append(homolog_result)
            
            # Pausa entre requests
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        self.results = results
        
        # Estadísticas finales
        print(f"\n📊 ESTADÍSTICAS DE HOMOLOGACIÓN")
        print("=" * 70)
        print(f"✅ Enfermedades procesadas: {len(results)}")
        print(f"🎯 Coincidencias encontradas: {successful_matches}")
        print(f"📈 Tasa de éxito: {(successful_matches/len(results)*100):.1f}%")
        
        return True
    
    def calculate_icd10_similarity(self, colombia_code, orphanet_codes):
        """Calcula similitud entre códigos ICD-10"""
        if not orphanet_codes:
            return 0.0
        
        colombia_code = str(colombia_code).upper().strip()
        max_similarity = 0.0
        
        for orpha_code in orphanet_codes:
            orpha_code = str(orpha_code).upper().strip()
            
            # Coincidencia exacta
            if colombia_code == orpha_code:
                return 1.0
            
            # Similitud por categoría (primera letra)
            if colombia_code[0] == orpha_code[0]:
                max_similarity = max(max_similarity, 0.5)
            
            # Similitud por subcategoría (primeros 3 caracteres)
            if len(colombia_code) >= 3 and len(orpha_code) >= 3:
                if colombia_code[:3] == orpha_code[:3]:
                    max_similarity = max(max_similarity, 0.8)
        
        return max_similarity
    
    def generate_homologation_report(self):
        """Genera reporte de homologación"""
        if not self.results:
            print("❌ No hay resultados para reportar")
            return
        
        # Crear DataFrame de resultados
        report_data = []
        
        for result in self.results:
            row = {
                "Número": result["numero"],
                "Nombre_Enfermedad": result["nombre_original"],
                "CIE10_Colombia": result["codigo_cie10_colombia"],
                "Estado_Homologación": result["homologation_status"],
                "Códigos_Orphá": ", ".join(result["orphanet_search"].get("orpha_codes", [])),
                "CIE10_Orphanet": ", ".join(result["orphanet_search"].get("icd10_codes", [])),
                "Coincidencia_CIE10": result.get("icd10_match", False),
                "Similitud_CIE10": result.get("icd10_similarity", 0.0),
                "Observaciones_Originales": result["observaciones"]
            }
            report_data.append(row)
        
        report_df = pd.DataFrame(report_data)
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"homologacion_orphanet_colombia_{timestamp}.csv"
        
        report_df.to_csv(report_filename, index=False, encoding='utf-8')
        print(f"💾 Reporte guardado: {report_filename}")
        
        # Estadísticas del reporte
        total = len(report_df)
        found = len(report_df[report_df["Estado_Homologación"] == "FOUND"])
        exact_matches = len(report_df[report_df["Coincidencia_CIE10"] == True])
        high_similarity = len(report_df[report_df["Similitud_CIE10"] >= 0.8])
        
        print(f"\n📈 RESUMEN DEL REPORTE")
        print("-" * 50)
        print(f"📋 Total procesado: {total}")
        print(f"✅ Encontradas en Orphanet: {found} ({found/total*100:.1f}%)")
        print(f"🎯 Coincidencias exactas CIE-10: {exact_matches} ({exact_matches/total*100:.1f}%)")
        print(f"⭐ Alta similitud CIE-10: {high_similarity} ({high_similarity/total*100:.1f}%)")
        
        return report_filename
    
    def save_detailed_results(self):
        """Guarda resultados detallados en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"homologacion_detallada_{timestamp}.json"
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados detallados guardados: {json_filename}")
        return json_filename

def main():
    """Función principal de homologación"""
    print("=" * 80)
    print("🔍 HOMOLOGACIÓN ORPHANET - ENFERMEDADES RARAS COLOMBIA")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Ruta al CSV de enfermedades raras de Colombia
    csv_path = "enfermedades_raras_colombia_2023_corregido.csv"
    
    try:
        # Inicializar homologador
        homologator = OrphanetHomologator(csv_path)
        
        # Cargar dataset
        if not homologator.load_dataset():
            return
        
        # Procesar muestra (ajustar sample_size según necesidad)
        sample_size = 20  # Empezar con muestra pequeña
        print(f"\n🎯 Procesando muestra de {sample_size} enfermedades")
        print("⏰ Esto tomará aproximadamente {:.1f} minutos".format(sample_size * DELAY_BETWEEN_REQUESTS / 60))
        
        if homologator.process_sample(sample_size):
            # Generar reportes
            homologator.generate_homologation_report()
            homologator.save_detailed_results()
            
            print(f"\n🎉 HOMOLOGACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            
        else:
            print("❌ Error en el proceso de homologación")
            
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
