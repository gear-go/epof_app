#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOMOLOGACIÓN MASIVA POR LOTES - COLOMBIA ↔ ORPHANET
Procesa todas las enfermedades del CSV Colombia en grupos manejables

Características:
- Procesamiento por lotes de 100-200 enfermedades
- Guardado automático de resultados parciales
- Reanudación desde último punto procesado
- Monitoreo de progreso en tiempo real
- Control de rate limiting para no sobrecargar Orphanet
"""

import pandas as pd
import requests
import time
import os
import json
from datetime import datetime, timedelta
import re
from urllib.parse import quote
import argparse
import sys

class HomologadorMasivo:
    def __init__(self, archivo_csv, tamano_lote=150, delay_request=1.2, carpeta_resultados="resultados_homologacion"):
        self.archivo_csv = archivo_csv
        self.tamano_lote = tamano_lote
        self.delay_request = delay_request
        self.carpeta_resultados = carpeta_resultados
        
        # Crear carpeta de resultados
        os.makedirs(carpeta_resultados, exist_ok=True)
        
        # Archivo de control de progreso
        self.archivo_progreso = os.path.join(carpeta_resultados, "progreso_homologacion.json")
        
        # Cargar dataset
        self.df_colombia = self.cargar_dataset()
        
        # Cargar progreso previo
        self.progreso = self.cargar_progreso()
        
        print(f"🚀 HomologadorMasivo inicializado")
        print(f"📊 Total enfermedades: {len(self.df_colombia)}")
        print(f"📦 Tamaño de lote: {tamano_lote}")
        print(f"⏱️  Delay por request: {delay_request}s")
        print(f"📁 Carpeta resultados: {carpeta_resultados}")
    
    def cargar_dataset(self):
        """Carga el dataset de Colombia"""
        try:
            df = pd.read_csv(self.archivo_csv, encoding='utf-8')
            print(f"✅ Dataset cargado: {len(df)} enfermedades")
            
            # Limpiar y estandarizar columnas
            df.columns = ['numero', 'nombre', 'codigo_cie10', 'observaciones']
            df = df.fillna('')
            
            return df
        except Exception as e:
            print(f"❌ Error cargando dataset: {e}")
            sys.exit(1)
    
    def cargar_progreso(self):
        """Carga el progreso previo si existe"""
        if os.path.exists(self.archivo_progreso):
            try:
                with open(self.archivo_progreso, 'r', encoding='utf-8') as f:
                    progreso = json.load(f)
                print(f"📋 Progreso previo encontrado: Lote {progreso.get('ultimo_lote', 0)}")
                return progreso
            except:
                print("⚠️  Error cargando progreso previo, iniciando desde cero")
        
        return {
            'ultimo_lote': 0,
            'total_procesados': 0,
            'total_matches': 0,
            'inicio_proceso': datetime.now().isoformat(),
            'lotes_completados': []
        }
    
    def guardar_progreso(self):
        """Guarda el progreso actual"""
        self.progreso['ultima_actualizacion'] = datetime.now().isoformat()
        try:
            with open(self.archivo_progreso, 'w', encoding='utf-8') as f:
                json.dump(self.progreso, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Error guardando progreso: {e}")
    
    def buscar_en_orphanet_avanzado(self, nombre_enfermedad, numero_colombia):
        """
        Búsqueda avanzada en Orphanet usando múltiples estrategias
        """
        resultados = {
            'numero_colombia': numero_colombia,
            'nombre_colombia': nombre_enfermedad,
            'encontrado': False,
            'orpha_number': None,
            'orpha_url': None,
            'nombre_orphanet': None,
            'codigos_cie10_orphanet': [],
            'metodo_encontrado': None,
            'similitud_nombre': 0,
            'error': None
        }
        
        try:
            # Estrategia 1: Búsqueda directa por nombre
            resultado = self.buscar_por_nombre_directo(nombre_enfermedad)
            if resultado['encontrado']:
                resultados.update(resultado)
                resultados['metodo_encontrado'] = 'nombre_directo'
                return resultados
            
            # Estrategia 2: Búsqueda por nombre simplificado
            nombre_simple = self.simplificar_nombre(nombre_enfermedad)
            if nombre_simple != nombre_enfermedad:
                resultado = self.buscar_por_nombre_directo(nombre_simple)
                if resultado['encontrado']:
                    resultados.update(resultado)
                    resultados['metodo_encontrado'] = 'nombre_simplificado'
                    return resultados
            
            # Estrategia 3: Búsqueda por partes del nombre
            partes = self.extraer_partes_nombre(nombre_enfermedad)
            for parte in partes:
                if len(parte) > 5:  # Solo buscar partes significativas
                    resultado = self.buscar_por_nombre_directo(parte)
                    if resultado['encontrado']:
                        # Verificar similitud antes de aceptar
                        similitud = self.calcular_similitud_nombres(nombre_enfermedad, resultado.get('nombre_orphanet', ''))
                        if similitud > 0.6:
                            resultados.update(resultado)
                            resultados['metodo_encontrado'] = f'parte_nombre_{parte[:20]}'
                            resultados['similitud_nombre'] = similitud
                            return resultados
            
            # No encontrado por ningún método
            resultados['error'] = 'No encontrado por ningún método de búsqueda'
            return resultados
            
        except Exception as e:
            resultados['error'] = str(e)
            return resultados
    
    def buscar_por_nombre_directo(self, termino_busqueda):
        """Búsqueda directa en Orphanet"""
        resultado = {
            'encontrado': False,
            'orpha_number': None,
            'orpha_url': None,
            'nombre_orphanet': None,
            'codigos_cie10_orphanet': []
        }
        
        try:
            # URL de búsqueda en español
            termino_encoded = quote(termino_busqueda)
            url_busqueda = f"https://www.orpha.net/es/disease/search?query={termino_encoded}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url_busqueda, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                contenido = response.text
                
                # Buscar enlaces a páginas de detalle
                patron_enlaces = r'href="[^"]*disease/detail/(\d+)[^"]*"[^>]*>([^<]+)</a>'
                matches = re.findall(patron_enlaces, contenido, re.IGNORECASE)
                
                if matches:
                    # Tomar el primer resultado (más relevante)
                    orpha_num, nombre_encontrado = matches[0]
                    
                    # Verificar el detalle de la enfermedad
                    url_detalle = f"https://www.orpha.net/es/disease/detail/{orpha_num}"
                    detalles = self.obtener_detalles_orphanet(url_detalle)
                    
                    if detalles['exitoso']:
                        resultado.update({
                            'encontrado': True,
                            'orpha_number': int(orpha_num),
                            'orpha_url': url_detalle,
                            'nombre_orphanet': detalles.get('nombre', nombre_encontrado.strip()),
                            'codigos_cie10_orphanet': detalles.get('codigos_cie10', [])
                        })
            
            return resultado
            
        except Exception as e:
            resultado['error'] = str(e)
            return resultado
    
    def obtener_detalles_orphanet(self, url_detalle):
        """Obtiene detalles de una página específica de Orphanet"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es,en;q=0.5',
            }
            
            response = requests.get(url_detalle, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                contenido = response.text
                
                # Extraer nombre
                patrones_nombre = [
                    r'<h1[^>]*>([^<]+)</h1>',
                    r'<h2[^>]*>([^<]+)</h2>',
                    r'<title>([^<]+?)\s*-\s*Orphanet</title>'
                ]
                
                nombre = "No encontrado"
                for patron in patrones_nombre:
                    match = re.search(patron, contenido, re.IGNORECASE | re.DOTALL)
                    if match:
                        nombre = match.group(1).strip()
                        nombre = re.sub(r'\s+', ' ', nombre)
                        break
                
                # Extraer códigos CIE-10
                codigos_cie10 = self.extraer_codigos_cie10(contenido)
                
                return {
                    'exitoso': True,
                    'nombre': nombre,
                    'codigos_cie10': codigos_cie10
                }
            else:
                return {'exitoso': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'exitoso': False, 'error': str(e)}
    
    def extraer_codigos_cie10(self, contenido_html):
        """Extrae códigos CIE-10 válidos del contenido HTML"""
        patrones = [
            r'ICD-?10[:\s]*([A-Z]\d{2}[\.\d]*)',
            r'CIE-?10[:\s]*([A-Z]\d{2}[\.\d]*)',
            r'([A-Z]\d{2}\.\d+)',
            r'([A-Z]\d{2})'
        ]
        
        codigos = []
        for patron in patrones:
            matches = re.findall(patron, contenido_html, re.IGNORECASE)
            codigos.extend(matches)
        
        # Filtrar y limpiar códigos válidos
        codigos_validos = []
        for codigo in codigos:
            codigo = codigo.upper().strip()
            if self.es_codigo_cie10_valido(codigo):
                codigos_validos.append(codigo)
        
        return list(set(codigos_validos))  # Eliminar duplicados
    
    def es_codigo_cie10_valido(self, codigo):
        """Valida si un código CIE-10 es válido"""
        if not codigo or len(codigo) < 3:
            return False
        
        # Debe empezar con letra seguida de números
        if not re.match(r'^[A-Z]\d{2}', codigo):
            return False
        
        # Evitar códigos genéricos o de ejemplo
        codigos_invalidos = ['A00', 'B00', 'Z99', 'X99', 'Y99']
        if any(codigo.startswith(inv) for inv in codigos_invalidos):
            return False
        
        return True
    
    def simplificar_nombre(self, nombre):
        """Simplifica un nombre para mejorar la búsqueda"""
        # Remover prefijos comunes
        prefijos = [
            'síndrome de ', 'sindrome de ', 'enfermedad de ',
            'deficiencia de ', 'defecto de ', 'trastorno de ',
            'displasia ', 'distrofia ', 'atrofia '
        ]
        
        nombre_lower = nombre.lower()
        for prefijo in prefijos:
            if nombre_lower.startswith(prefijo):
                nombre = nombre[len(prefijo):].strip()
                break
        
        # Limpiar caracteres especiales
        nombre = re.sub(r'[^\w\s\-]', ' ', nombre)
        nombre = re.sub(r'\s+', ' ', nombre).strip()
        
        return nombre
    
    def extraer_partes_nombre(self, nombre):
        """Extrae partes significativas del nombre para búsqueda"""
        # Dividir por palabras clave
        partes = []
        
        # Buscar nombres propios (apellidos/nombres de síndromes)
        nombres_propios = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', nombre)
        partes.extend(nombres_propios)
        
        # Buscar términos médicos comunes
        terminos_medicos = re.findall(r'\b(?:aciduria|acidemia|deficiencia|síndrome|displasia|distrofia|atrofia)\b', nombre.lower())
        partes.extend(terminos_medicos)
        
        return list(set(partes))
    
    def calcular_similitud_nombres(self, nombre1, nombre2):
        """Calcula similitud básica entre nombres"""
        if not nombre1 or not nombre2:
            return 0
        
        n1 = self.normalizar_texto(nombre1)
        n2 = self.normalizar_texto(nombre2)
        
        if n1 == n2:
            return 1.0
        
        if n1 in n2 or n2 in n1:
            return 0.8
        
        # Similitud por palabras comunes
        palabras1 = set(n1.split())
        palabras2 = set(n2.split())
        
        if palabras1 and palabras2:
            comunes = palabras1.intersection(palabras2)
            total = palabras1.union(palabras2)
            return len(comunes) / len(total)
        
        return 0
    
    def normalizar_texto(self, texto):
        """Normaliza texto para comparación"""
        if not texto:
            return ""
        
        texto = texto.lower()
        
        # Remover acentos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u', 'ç': 'c'
        }
        
        for old, new in replacements.items():
            texto = texto.replace(old, new)
        
        # Limpiar caracteres especiales
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def procesar_lote(self, numero_lote):
        """Procesa un lote específico de enfermedades"""
        inicio_idx = numero_lote * self.tamano_lote
        fin_idx = min((numero_lote + 1) * self.tamano_lote, len(self.df_colombia))
        
        if inicio_idx >= len(self.df_colombia):
            return None
        
        lote = self.df_colombia.iloc[inicio_idx:fin_idx]
        
        print(f"\n🔄 PROCESANDO LOTE {numero_lote + 1}")
        print(f"📊 Registros: {inicio_idx + 1} a {fin_idx} ({len(lote)} enfermedades)")
        print("-" * 60)
        
        resultados = []
        matches_encontrados = 0
        inicio_lote = time.time()
        
        for i, (idx, enfermedad) in enumerate(lote.iterrows()):
            numero = enfermedad['numero']
            nombre = enfermedad['nombre']
            codigo_colombia = enfermedad['codigo_cie10']
            
            print(f"🔍 {inicio_idx + i + 1}/{len(self.df_colombia)}: {nombre[:50]}...", end=" ")
            
            # Buscar en Orphanet
            resultado = self.buscar_en_orphanet_avanzado(nombre, numero)
            
            if resultado['encontrado']:
                matches_encontrados += 1
                print(f"✅ MATCH - ORPHA:{resultado['orpha_number']}")
            else:
                print(f"❌ No encontrado")
            
            # Agregar datos de Colombia al resultado
            resultado.update({
                'codigo_cie10_colombia': codigo_colombia,
                'observaciones_colombia': enfermedad.get('observaciones', '')
            })
            
            resultados.append(resultado)
            
            # Delay para no sobrecargar el servidor
            time.sleep(self.delay_request)
        
        # Guardar resultados del lote
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_lote = os.path.join(
            self.carpeta_resultados, 
            f"lote_{numero_lote + 1:03d}_{timestamp}.csv"
        )
        
        df_resultados = pd.DataFrame(resultados)
        df_resultados.to_csv(archivo_lote, index=False, encoding='utf-8')
        
        fin_lote = time.time()
        duracion = fin_lote - inicio_lote
        
        print(f"\n📊 LOTE {numero_lote + 1} COMPLETADO:")
        print(f"✅ Matches encontrados: {matches_encontrados}/{len(lote)}")
        print(f"⏱️  Tiempo: {duracion/60:.1f} minutos")
        print(f"📄 Guardado: {archivo_lote}")
        
        # Actualizar progreso
        self.progreso['ultimo_lote'] = numero_lote + 1
        self.progreso['total_procesados'] += len(lote)
        self.progreso['total_matches'] += matches_encontrados
        self.progreso['lotes_completados'].append({
            'numero': numero_lote + 1,
            'archivo': archivo_lote,
            'matches': matches_encontrados,
            'total': len(lote),
            'timestamp': timestamp
        })
        
        self.guardar_progreso()
        
        return {
            'numero_lote': numero_lote + 1,
            'matches': matches_encontrados,
            'total': len(lote),
            'archivo': archivo_lote
        }
    
    def ejecutar_homologacion_completa(self, lotes_maximos=None):
        """Ejecuta la homologación completa por lotes"""
        print("=" * 80)
        print("🚀 HOMOLOGACIÓN MASIVA COMPLETA - COLOMBIA ↔ ORPHANET")
        print("=" * 80)
        
        total_lotes = (len(self.df_colombia) + self.tamano_lote - 1) // self.tamano_lote
        lote_inicio = self.progreso['ultimo_lote']
        
        if lotes_maximos:
            total_lotes = min(total_lotes, lote_inicio + lotes_maximos)
        
        print(f"📊 CONFIGURACIÓN:")
        print(f"📋 Total enfermedades: {len(self.df_colombia)}")
        print(f"📦 Tamaño de lote: {self.tamano_lote}")
        print(f"🎯 Total lotes: {total_lotes}")
        print(f"🔄 Lote inicial: {lote_inicio + 1}")
        print(f"⏱️  Tiempo estimado: {(total_lotes - lote_inicio) * self.tamano_lote * self.delay_request / 60:.1f} minutos")
        
        if lote_inicio > 0:
            print(f"📈 Progreso previo: {self.progreso['total_procesados']} procesados, {self.progreso['total_matches']} matches")
        
        # Confirmar inicio
        respuesta = input(f"\n¿Continuar con la homologación? (s/N): ").strip().lower()
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
        
        inicio_total = time.time()
        
        try:
            for numero_lote in range(lote_inicio, total_lotes):
                resultado_lote = self.procesar_lote(numero_lote)
                
                if resultado_lote is None:
                    break
                
                # Mostrar progreso general
                progreso_pct = ((numero_lote + 1) / total_lotes) * 100
                print(f"\n📈 PROGRESO GENERAL: {progreso_pct:.1f}% ({numero_lote + 1}/{total_lotes} lotes)")
                print(f"🎯 Total matches acumulados: {self.progreso['total_matches']}")
                
                # Pausa entre lotes para no sobrecargar
                if numero_lote < total_lotes - 1:
                    print(f"⏸️  Pausa de 30 segundos antes del siguiente lote...")
                    time.sleep(30)
        
        except KeyboardInterrupt:
            print(f"\n⏸️  PROCESO INTERRUMPIDO POR USUARIO")
            print(f"📊 Progreso guardado hasta lote {self.progreso['ultimo_lote']}")
            return
        
        except Exception as e:
            print(f"\n❌ ERROR EN PROCESAMIENTO: {e}")
            print(f"📊 Progreso guardado hasta lote {self.progreso['ultimo_lote']}")
            return
        
        fin_total = time.time()
        duracion_total = (fin_total - inicio_total) / 60
        
        print(f"\n" + "=" * 80)
        print(f"✅ HOMOLOGACIÓN MASIVA COMPLETADA")
        print(f"⏱️  Tiempo total: {duracion_total:.1f} minutos")
        print(f"📋 Total procesados: {self.progreso['total_procesados']}")
        print(f"🎯 Total matches: {self.progreso['total_matches']}")
        print(f"📈 Tasa de éxito: {(self.progreso['total_matches']/self.progreso['total_procesados']*100):.1f}%")
        print(f"📁 Resultados en: {self.carpeta_resultados}")
        print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Homologación masiva Colombia ↔ Orphanet")
    parser.add_argument("--csv", default="enfermedades_raras_colombia_2023_corregido.csv", help="Archivo CSV de entrada")
    parser.add_argument("--lote", type=int, default=150, help="Tamaño del lote")
    parser.add_argument("--delay", type=float, default=1.2, help="Delay entre requests")
    parser.add_argument("--max-lotes", type=int, help="Máximo número de lotes a procesar")
    
    args = parser.parse_args()
    
    # Crear homologador
    homologador = HomologadorMasivo(
        archivo_csv=args.csv,
        tamano_lote=args.lote,
        delay_request=args.delay
    )
    
    # Ejecutar homologación
    homologador.ejecutar_homologacion_completa(lotes_maximos=args.max_lotes)

if __name__ == "__main__":
    main()
