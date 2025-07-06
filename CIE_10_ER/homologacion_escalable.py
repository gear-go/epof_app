#!/usr/bin/env python3
"""
HOMOLOGACIÓN ORPHANET ESCALABLE
Basada en estrategia exitosa: acceso directo a URLs de detalle

Estrategia probada exitosa:
1. Buscar ranges de números ORPHA
2. Acceder directamente a páginas de detalle
3. Extraer nombres y códigos CIE-10
4. Comparar con dataset Colombia

Flujo: Enumerar ORPHA → Extraer datos → Comparar con Colombia
"""

import pandas as pd
import requests
import time
from datetime import datetime
import re
import json

class OrphanetHomologadorEscalable:
    """Homologador escalable basado en estrategia exitosa"""
    
    def __init__(self, csv_colombia):
        self.df_colombia = pd.read_csv(csv_colombia)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "OrphanetHomologation/Final"})
        self.resultados = []
        self.contador_exitos = 0
        self.contador_errores = 0
        
    def homologar_dataset_completo(self, muestra=100):
        """Homologa usando estrategia de búsqueda inteligente"""
        print("=" * 80)
        print("🚀 HOMOLOGACIÓN ESCALABLE ORPHANET → COLOMBIA")
        print("=" * 80)
        print(f"📊 Dataset Colombia: {len(self.df_colombia)} enfermedades")
        print(f"🎯 Procesando muestra: {muestra} enfermedades")
        print("=" * 80)
        
        # Crear índice de búsqueda rápida de Colombia
        self.crear_indice_colombia()
        
        # Estrategia: explorar rangos conocidos de ORPHA
        rangos_orpha = [
            range(1, 100),      # Rango inicial
            range(900, 1000),   # Rango donde encontramos Acondrogénesis (932)
            range(1000, 1100),  # Rango siguiente
            range(100, 200),    # Otro rango inicial
            range(500, 600)     # Rango medio
        ]
        
        enfermedades_procesadas = 0
        
        for rango in rangos_orpha:
            if enfermedades_procesadas >= muestra:
                break
                
            print(f"\n🔍 Explorando rango ORPHA {rango.start}-{rango.stop-1}")
            
            for orpha_num in rango:
                if enfermedades_procesadas >= muestra:
                    break
                    
                resultado = self.procesar_orpha_individual(orpha_num)
                
                if resultado.get('exito') and resultado.get('tiene_match_colombia'):
                    enfermedades_procesadas += 1
                    print(f"   ✅ ORPHA:{orpha_num} → {resultado['nombre_orphanet']} → MATCH Colombia")
                    self.resultados.append(resultado)
                elif resultado.get('exito'):
                    print(f"   📝 ORPHA:{orpha_num} → {resultado['nombre_orphanet']} (sin match Colombia)")
                
                time.sleep(0.3)  # Pausa corta entre requests
        
        self.generar_reporte_final()
    
    def crear_indice_colombia(self):
        """Crea índice para búsqueda rápida en dataset Colombia"""
        self.indice_nombres = {}
        self.indice_codigos = {}
        
        for idx, row in self.df_colombia.iterrows():
            # Índice por nombre normalizado
            nombre_norm = self.normalizar_nombre(row['Nombre_Enfermedad'])
            self.indice_nombres[nombre_norm] = row
            
            # Índice por código CIE-10
            codigo = str(row['Código_CIE10']).strip().upper()
            if codigo not in self.indice_codigos:
                self.indice_codigos[codigo] = []
            self.indice_codigos[codigo].append(row)
        
        print(f"📋 Índice creado: {len(self.indice_nombres)} nombres, {len(self.indice_codigos)} códigos únicos")
    
    def procesar_orpha_individual(self, orpha_number):
        """Procesa una enfermedad ORPHA individual"""
        try:
            url = f"https://www.orpha.net/es/disease/detail/{orpha_number}"
            response = self.session.get(url, timeout=8, verify=False)
            
            if response.status_code == 200:
                # Extraer datos de Orphanet
                datos_orphanet = self.extraer_datos_orphanet(response.text, orpha_number)
                
                if datos_orphanet['valido']:
                    # Buscar matches en Colombia
                    matches_colombia = self.buscar_matches_colombia(datos_orphanet)
                    
                    resultado = {
                        'orpha_number': orpha_number,
                        'url': url,
                        'exito': True,
                        'nombre_orphanet': datos_orphanet['nombre'],
                        'codigo_cie10_orphanet': datos_orphanet['codigo_cie10'],
                        'matches_colombia': matches_colombia,
                        'tiene_match_colombia': len(matches_colombia) > 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.contador_exitos += 1
                    return resultado
                else:
                    return {'orpha_number': orpha_number, 'exito': False, 'error': 'Datos no válidos'}
            else:
                return {'orpha_number': orpha_number, 'exito': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.contador_errores += 1
            return {'orpha_number': orpha_number, 'exito': False, 'error': str(e)}
    
    def extraer_datos_orphanet(self, html_content, orpha_number):
        """Extrae datos estructurados de página Orphanet"""
        datos = {
            'valido': False,
            'nombre': '',
            'codigo_cie10': '',
            'sinonimos': []
        }
        
        try:
            # Extraer nombre principal
            title_patterns = [
                r'<title>Orphanet:\s*([^<]+)</title>',
                r'<h1[^>]*>([^<]+)</h1>',
                r'Orphanet:\s*([^\n\r]+)'
            ]
            
            for pattern in title_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    datos['nombre'] = matches[0].strip()
                    break
            
            # Extraer código CIE-10 con múltiples patrones
            cie10_patterns = [
                r'CIE-?10[:\s]*([A-Z]\d{2}\.?\d{0,2})',
                r'ICD-?10[:\s]*([A-Z]\d{2}\.?\d{0,2})',
                r'Código[:\s]*([A-Z]\d{2}\.?\d{0,2})'
            ]
            
            for pattern in cie10_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    codigo_encontrado = matches[0].strip()
                    if self.es_codigo_cie10_valido(codigo_encontrado):
                        datos['codigo_cie10'] = codigo_encontrado
                        break
            
            # Validar si tenemos datos mínimos
            if datos['nombre'] and len(datos['nombre']) > 3:
                datos['valido'] = True
            
            # Verificar que sea realmente una enfermedad (no página de error)
            indicadores_validos = ['enfermedad', 'síndrome', 'trastorno', 'orpha', 'prevalencia']
            contenido_lower = html_content.lower()
            
            if not any(ind in contenido_lower for ind in indicadores_validos):
                datos['valido'] = False
            
        except Exception as e:
            datos['error'] = str(e)
        
        return datos
    
    def buscar_matches_colombia(self, datos_orphanet):
        """Busca coincidencias en dataset Colombia"""
        matches = []
        
        # Búsqueda por nombre
        nombre_norm = self.normalizar_nombre(datos_orphanet['nombre'])
        if nombre_norm in self.indice_nombres:
            match = self.indice_nombres[nombre_norm].copy()
            match['tipo_match'] = 'nombre_exacto'
            match['similitud'] = 1.0
            matches.append(match)
        
        # Búsqueda por código CIE-10
        if datos_orphanet['codigo_cie10']:
            codigo_orphanet = datos_orphanet['codigo_cie10'].upper().strip()
            
            # Búsqueda exacta
            if codigo_orphanet in self.indice_codigos:
                for row_colombia in self.indice_codigos[codigo_orphanet]:
                    match = row_colombia.copy()
                    match['tipo_match'] = 'codigo_exacto'
                    match['similitud'] = 1.0
                    matches.append(match)
            else:
                # Búsqueda por similitud de código
                for codigo_colombia in self.indice_codigos.keys():
                    similitud = self.calcular_similitud_codigo(codigo_orphanet, codigo_colombia)
                    if similitud >= 0.7:  # Alta similitud
                        for row_colombia in self.indice_codigos[codigo_colombia]:
                            match = row_colombia.copy()
                            match['tipo_match'] = 'codigo_similar'
                            match['similitud'] = similitud
                            matches.append(match)
        
        # Búsqueda por similitud de nombre
        if not matches:
            matches.extend(self.buscar_por_similitud_nombre(datos_orphanet['nombre']))
        
        return matches
    
    def normalizar_nombre(self, nombre):
        """Normaliza nombre para comparación"""
        if not nombre:
            return ""
        
        nombre = str(nombre).lower().strip()
        
        # Remover prefijos comunes
        prefijos = ['síndrome de ', 'sindrome de ', 'enfermedad de ', 'trastorno de ']
        for prefijo in prefijos:
            if nombre.startswith(prefijo):
                nombre = nombre[len(prefijo):].strip()
                break
        
        # Normalizar caracteres
        nombre = re.sub(r'[^\w\s]', ' ', nombre)
        nombre = re.sub(r'\s+', ' ', nombre).strip()
        
        return nombre
    
    def buscar_por_similitud_nombre(self, nombre_orphanet):
        """Busca por similitud de nombre"""
        matches = []
        nombre_norm = self.normalizar_nombre(nombre_orphanet)
        
        if len(nombre_norm) < 3:
            return matches
        
        # Buscar nombres que contengan palabras clave
        palabras_clave = nombre_norm.split()[:3]  # Primeras 3 palabras
        
        for nombre_colombia_norm, row_colombia in self.indice_nombres.items():
            similitud = self.calcular_similitud_nombre(nombre_norm, nombre_colombia_norm)
            if similitud >= 0.6:  # Similitud moderada
                match = row_colombia.copy()
                match['tipo_match'] = 'nombre_similar'
                match['similitud'] = similitud
                matches.append(match)
        
        return matches[:3]  # Máximo 3 matches por similitud
    
    def calcular_similitud_nombre(self, nombre1, nombre2):
        """Calcula similitud entre nombres"""
        if not nombre1 or not nombre2:
            return 0.0
        
        palabras1 = set(nombre1.split())
        palabras2 = set(nombre2.split())
        
        if not palabras1 or not palabras2:
            return 0.0
        
        interseccion = palabras1.intersection(palabras2)
        union = palabras1.union(palabras2)
        
        return len(interseccion) / len(union) if union else 0.0
    
    def calcular_similitud_codigo(self, codigo1, codigo2):
        """Calcula similitud entre códigos CIE-10"""
        if codigo1 == codigo2:
            return 1.0
        
        if codigo1[0] == codigo2[0]:  # Misma categoría principal
            if len(codigo1) >= 3 and len(codigo2) >= 3:
                if codigo1[:3] == codigo2[:3]:  # Misma subcategoría
                    return 0.8
                else:
                    return 0.3
        
        return 0.0
    
    def es_codigo_cie10_valido(self, codigo):
        """Valida código CIE-10"""
        if not codigo or len(codigo) < 3:
            return False
        return re.match(r'^[A-Z]\d{2}', codigo) is not None
    
    def generar_reporte_final(self):
        """Genera reporte final de homologación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"homologacion_orphanet_escalable_{timestamp}.csv"
        
        # Preparar datos para CSV
        datos_reporte = []
        
        for resultado in self.resultados:
            for match in resultado.get('matches_colombia', []):
                fila = {
                    'ORPHA_Number': resultado['orpha_number'],
                    'ORPHA_URL': resultado['url'],
                    'Nombre_Orphanet': resultado['nombre_orphanet'],
                    'CIE10_Orphanet': resultado['codigo_cie10_orphanet'],
                    'Numero_Colombia': match.get('Número', ''),
                    'Nombre_Colombia': match.get('Nombre_Enfermedad', ''),
                    'CIE10_Colombia': match.get('Código_CIE10', ''),
                    'Tipo_Match': match.get('tipo_match', ''),
                    'Similitud': match.get('similitud', 0.0),
                    'Observaciones_Colombia': match.get('Observaciones', '')
                }
                datos_reporte.append(fila)
        
        # Guardar CSV
        if datos_reporte:
            df_reporte = pd.DataFrame(datos_reporte)
            df_reporte.to_csv(filename, index=False, encoding='utf-8')
            
            print(f"\n📊 REPORTE FINAL GENERADO: {filename}")
            print("=" * 80)
            print(f"✅ Matches encontrados: {len(datos_reporte)}")
            print(f"🎯 ORPHA únicos con matches: {len(self.resultados)}")
            print(f"📈 Tasa de éxito: {self.contador_exitos}/{self.contador_exitos + self.contador_errores}")
            
            # Estadísticas por tipo de match
            tipos_match = df_reporte['Tipo_Match'].value_counts()
            print(f"\n📋 TIPOS DE COINCIDENCIAS:")
            for tipo, cantidad in tipos_match.items():
                print(f"   {tipo}: {cantidad}")
        else:
            print(f"\n⚠️ No se encontraron matches para generar reporte")

def main():
    """Función principal"""
    print("🚀 Iniciando homologación escalable Orphanet")
    
    csv_colombia = "enfermedades_raras_colombia_2023_corregido.csv"
    
    homologador = OrphanetHomologadorEscalable(csv_colombia)
    homologador.homologar_dataset_completo(muestra=30)  # Muestra inicial

if __name__ == "__main__":
    main()
