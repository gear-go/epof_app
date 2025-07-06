#!/usr/bin/env python3
"""
Script para extraer códigos CIE-10 y enfermedades raras del PDF de la Resolución No. 023 de 2023
Basado en las especificaciones del archivo context.md
"""

import PyPDF2
import re
import csv
import os
from typing import List, Tuple, Dict

class ExtractorCIE10:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.texto_completo = ""
        self.enfermedades = []
        
    def extraer_texto_pdf(self) -> str:
        """Extrae todo el texto del PDF"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                texto = ""
                
                print(f"Procesando {len(pdf_reader.pages)} páginas...")
                
                for num_pagina, pagina in enumerate(pdf_reader.pages, 1):
                    try:
                        texto_pagina = pagina.extract_text()
                        texto += texto_pagina + "\n"
                        print(f"Página {num_pagina} procesada")
                    except Exception as e:
                        print(f"Error en página {num_pagina}: {e}")
                
                self.texto_completo = texto
                return texto
                
        except Exception as e:
            print(f"Error al leer el PDF: {e}")
            return ""
    
    def validar_codigo_cie10(self, codigo: str) -> bool:
        """
        Valida si un código cumple con el formato CIE-10:
        [Letra][Dígito][Dígito][Dígito o X]
        """
        if not codigo or len(codigo) != 4:
            return False
        
        # Primer carácter debe ser letra mayúscula
        if not codigo[0].isupper() or not codigo[0].isalpha():
            return False
        
        # Siguientes 2 caracteres deben ser dígitos
        if not codigo[1:3].isdigit():
            return False
        
        # Último carácter debe ser dígito o X
        if not (codigo[3].isdigit() or codigo[3] == 'X'):
            return False
        
        return True
    
    def buscar_patrones_cie10(self, texto: str) -> List[str]:
        """Busca patrones que podrían ser códigos CIE-10"""
        # Patrón para códigos CIE-10: Letra + 3 dígitos/X
        patron = re.compile(r'\b[A-Z]\d{2}[\dX]\b')
        coincidencias = patron.findall(texto)
        
        # Filtrar solo códigos válidos
        codigos_validos = [codigo for codigo in coincidencias if self.validar_codigo_cie10(codigo)]
        
        return list(set(codigos_validos))  # Eliminar duplicados
    
    def extraer_enfermedades_y_codigos(self, texto: str) -> List[Dict]:
        """
        Extrae enfermedades y sus códigos CIE-10 del texto
        Busca patrones como números seguidos de nombre de enfermedad y posible código
        """
        lineas = texto.split('\n')
        enfermedades = []
        numero_actual = 0
        
        # Patrón para líneas que empiezan con número (posibles enfermedades)
        patron_numeracion = re.compile(r'^\s*(\d+)[\.\)]\s*(.+)', re.MULTILINE)
        
        # Patrón más flexible para capturar enfermedades
        patron_enfermedad = re.compile(r'(\d+)[\.\)\s]+([A-ZÁÉÍÓÚÑ][^0-9]*?)(?:\s+([A-Z]\d{2}[\dX]))?', re.IGNORECASE)
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            
            # Buscar coincidencias del patrón
            coincidencia = patron_enfermedad.search(linea)
            if coincidencia:
                numero = coincidencia.group(1)
                nombre_enfermedad = coincidencia.group(2).strip()
                codigo = coincidencia.group(3) if coincidencia.group(3) else None
                
                # Validar código si existe
                if codigo and not self.validar_codigo_cie10(codigo):
                    codigo = None
                
                # Limpiar nombre de enfermedad
                nombre_enfermedad = re.sub(r'\s+', ' ', nombre_enfermedad)
                nombre_enfermedad = nombre_enfermedad.strip('.,;')
                
                if nombre_enfermedad and len(nombre_enfermedad) > 3:
                    enfermedad = {
                        'numero': int(numero) if numero.isdigit() else len(enfermedades) + 1,
                        'nombre': nombre_enfermedad,
                        'codigo_cie10': codigo if codigo else 'XXXX',
                        'observaciones': 'Sin código asignado' if not codigo else ''
                    }
                    enfermedades.append(enfermedad)
        
        return enfermedades
    
    def buscar_enfermedades_alternativo(self, texto: str) -> List[Dict]:
        """
        Método alternativo para buscar enfermedades cuando el patrón principal falla
        """
        enfermedades = []
        
        # Buscar todos los códigos CIE-10 en el texto
        codigos_encontrados = self.buscar_patrones_cie10(texto)
        print(f"Códigos CIE-10 encontrados: {len(codigos_encontrados)}")
        print(f"Primeros 10 códigos: {codigos_encontrados[:10]}")
        
        # Buscar líneas con posibles enfermedades
        lineas = texto.split('\n')
        contador = 0
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if len(linea) < 10:  # Muy corta para ser una enfermedad
                continue
            
            # Buscar códigos CIE-10 en la línea
            codigos_en_linea = self.buscar_patrones_cie10(linea)
            
            if codigos_en_linea:
                # Extraer el nombre de la enfermedad (texto antes del código)
                for codigo in codigos_en_linea:
                    partes = linea.split(codigo)
                    if len(partes) >= 2:
                        nombre_candidato = partes[0].strip()
                        # Limpiar números de lista del inicio
                        nombre_candidato = re.sub(r'^\d+[\.\)]\s*', '', nombre_candidato)
                        
                        if len(nombre_candidato) > 5:
                            contador += 1
                            enfermedad = {
                                'numero': contador,
                                'nombre': nombre_candidato,
                                'codigo_cie10': codigo,
                                'observaciones': ''
                            }
                            enfermedades.append(enfermedad)
        
        return enfermedades
    
    def generar_csv(self, enfermedades: List[Dict], archivo_salida: str):
        """Genera el archivo CSV con las enfermedades y códigos"""
        try:
            with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
                campos = ['Número', 'Nombre_Enfermedad', 'Código_CIE10', 'Observaciones']
                writer = csv.DictWriter(csvfile, fieldnames=campos)
                
                # Escribir encabezados
                writer.writeheader()
                
                # Escribir datos
                for enfermedad in enfermedades:
                    writer.writerow({
                        'Número': enfermedad['numero'],
                        'Nombre_Enfermedad': enfermedad['nombre'],
                        'Código_CIE10': enfermedad['codigo_cie10'],
                        'Observaciones': enfermedad['observaciones']
                    })
            
            print(f"Archivo CSV generado: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"Error al generar CSV: {e}")
            return False
    
    def generar_reporte_calidad(self, enfermedades: List[Dict]) -> Dict:
        """Genera reporte de control de calidad"""
        total_enfermedades = len(enfermedades)
        con_codigo = len([e for e in enfermedades if e['codigo_cie10'] != 'XXXX'])
        sin_codigo = total_enfermedades - con_codigo
        
        codigos_unicos = set([e['codigo_cie10'] for e in enfermedades if e['codigo_cie10'] != 'XXXX'])
        
        reporte = {
            'total_enfermedades': total_enfermedades,
            'con_codigo_cie10': con_codigo,
            'sin_codigo_cie10': sin_codigo,
            'codigos_unicos': len(codigos_unicos),
            'codigos_lista': sorted(list(codigos_unicos))
        }
        
        return reporte
    
    def procesar(self) -> bool:
        """Método principal para procesar el PDF y generar el CSV"""
        print("=== EXTRACTOR DE CÓDIGOS CIE-10 ===")
        print(f"Procesando: {self.pdf_path}")
        
        # 1. Extraer texto del PDF
        print("\n1. Extrayendo texto del PDF...")
        texto = self.extraer_texto_pdf()
        
        if not texto:
            print("Error: No se pudo extraer texto del PDF")
            return False
        
        print(f"Texto extraído: {len(texto)} caracteres")
        
        # Guardar texto extraído para depuración
        with open('texto_extraido.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
        print("Texto guardado en 'texto_extraido.txt' para revisión")
        
        # 2. Extraer enfermedades y códigos
        print("\n2. Extrayendo enfermedades y códigos...")
        enfermedades = self.extraer_enfermedades_y_codigos(texto)
        
        if not enfermedades:
            print("No se encontraron enfermedades con el patrón principal. Probando método alternativo...")
            enfermedades = self.buscar_enfermedades_alternativo(texto)
        
        if not enfermedades:
            print("No se pudieron extraer enfermedades del documento")
            return False
        
        self.enfermedades = enfermedades
        
        # 3. Generar reporte de calidad
        print("\n3. Generando reporte de calidad...")
        reporte = self.generar_reporte_calidad(enfermedades)
        
        print(f"Total de enfermedades procesadas: {reporte['total_enfermedades']}")
        print(f"Con código CIE-10: {reporte['con_codigo_cie10']}")
        print(f"Sin código CIE-10: {reporte['sin_codigo_cie10']}")
        print(f"Códigos únicos encontrados: {reporte['codigos_unicos']}")
        
        # 4. Generar CSV
        print("\n4. Generando archivo CSV...")
        archivo_csv = "enfermedades_raras_cie10.csv"
        if self.generar_csv(enfermedades, archivo_csv):
            print(f"✅ Proceso completado exitosamente")
            print(f"📄 Archivo generado: {archivo_csv}")
            return True
        else:
            print("❌ Error al generar archivo CSV")
            return False

def main():
    """Función principal"""
    pdf_path = "Resolución No. 023 de 2023.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: No se encuentra el archivo {pdf_path}")
        return
    
    extractor = ExtractorCIE10(pdf_path)
    extractor.procesar()

if __name__ == "__main__":
    main()
