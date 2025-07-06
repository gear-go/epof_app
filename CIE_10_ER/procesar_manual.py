#!/usr/bin/env python3
"""
Script para procesar el archivo manual de enfermedades raras y huérfanas de Colombia
Corrige códigos que empiezan con 0 por Q y genera CSV según especificaciones de context.md
"""

import re
import csv
import pandas as pd
from typing import List, Dict, Tuple, Optional

def validar_codigo_cie10(codigo: str) -> bool:
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

def corregir_codigo_cero_a_q(codigo: str) -> str:
    """
    Corrige códigos que empiezan con 0 cambiándolos por Q
    """
    if codigo and len(codigo) == 4 and codigo[0] == '0':
        return 'Q' + codigo[1:]
    return codigo

def procesar_linea(linea: str, numero_linea: int) -> Optional[Dict]:
    """
    Procesa una línea del archivo de texto y extrae número, nombre y código
    """
    linea = linea.strip()
    if not linea:
        return None
    
    # Buscar patrón: número + nombre + código (al final)
    # El código CIE-10 estará al final de la línea
    partes = linea.split()
    
    if len(partes) < 2:
        return None
    
    # El último elemento debería ser el código
    posible_codigo = partes[-1]
    
    # Verificar si es un código CIE-10 (4 caracteres)
    if len(posible_codigo) == 4:
        # Extraer número (primer elemento)
        try:
            numero = int(partes[0])
        except ValueError:
            numero = numero_linea
        
        # El nombre está entre el número y el código
        nombre_partes = partes[1:-1]
        nombre = ' '.join(nombre_partes).strip()
        
        # Corregir código si empieza con 0
        codigo_original = posible_codigo
        codigo_corregido = corregir_codigo_cero_a_q(codigo_original)
        
        observaciones = ""
        if codigo_original != codigo_corregido:
            observaciones = f"Código corregido de {codigo_original} a {codigo_corregido}"
        
        return {
            'numero': numero,
            'nombre': nombre,
            'codigo_original': codigo_original,
            'codigo_cie10': codigo_corregido,
            'observaciones': observaciones
        }
    else:
        # Si no hay código válido al final, marcar como sin código
        try:
            numero = int(partes[0])
        except ValueError:
            numero = numero_linea
        
        nombre = ' '.join(partes[1:]).strip()
        
        return {
            'numero': numero,
            'nombre': nombre,
            'codigo_original': '',
            'codigo_cie10': 'XXXX',
            'observaciones': 'Sin código asignado'
        }

def procesar_archivo_manual(archivo_txt: str) -> List[Dict]:
    """
    Procesa el archivo de texto manual y extrae todas las enfermedades
    """
    enfermedades = []
    
    print(f"Procesando archivo: {archivo_txt}")
    
    try:
        with open(archivo_txt, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        print(f"Total de líneas a procesar: {len(lineas)}")
        
        for i, linea in enumerate(lineas, 1):
            resultado = procesar_linea(linea, i)
            if resultado and resultado['nombre']:  # Solo incluir si hay nombre
                enfermedades.append(resultado)
                
                # Mostrar progreso cada 100 líneas
                if i % 100 == 0:
                    print(f"Procesadas {i} líneas...")
        
        print(f"Total de enfermedades extraídas: {len(enfermedades)}")
        return enfermedades
        
    except Exception as e:
        print(f"Error al procesar archivo: {e}")
        return []

def generar_csv_corregido(enfermedades: List[Dict], archivo_salida: str):
    """
    Genera el archivo CSV con las enfermedades corregidas
    """
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
        
        print(f"✅ Archivo CSV generado: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"❌ Error al generar CSV: {e}")
        return False

def generar_reporte_correcciones(enfermedades: List[Dict]) -> Dict:
    """
    Genera un reporte de las correcciones realizadas
    """
    total_enfermedades = len(enfermedades)
    
    # Contar correcciones de códigos 0 -> Q
    correcciones_0_a_q = [e for e in enfermedades if e['codigo_original'] != e['codigo_cie10'] and e['codigo_original'].startswith('0')]
    
    # Contar códigos válidos
    codigos_validos = [e for e in enfermedades if validar_codigo_cie10(e['codigo_cie10'])]
    
    # Contar sin código
    sin_codigo = [e for e in enfermedades if e['codigo_cie10'] == 'XXXX']
    
    # Códigos únicos
    codigos_unicos = set([e['codigo_cie10'] for e in enfermedades if e['codigo_cie10'] != 'XXXX'])
    
    # Distribución por categorías
    categorias = {}
    for e in enfermedades:
        if e['codigo_cie10'] != 'XXXX':
            letra = e['codigo_cie10'][0]
            categorias[letra] = categorias.get(letra, 0) + 1
    
    reporte = {
        'total_enfermedades': total_enfermedades,
        'correcciones_0_a_q': len(correcciones_0_a_q),
        'codigos_validos': len(codigos_validos),
        'sin_codigo': len(sin_codigo),
        'codigos_unicos': len(codigos_unicos),
        'categorias': categorias,
        'lista_correcciones': correcciones_0_a_q
    }
    
    return reporte

def main():
    """Función principal"""
    archivo_txt = "enfermedades_raras_huerfanas_listado_2023_colombia.txt"
    archivo_csv = "enfermedades_raras_colombia_2023_corregido.csv"
    
    print("=== PROCESADOR DE ENFERMEDADES RARAS COLOMBIA 2023 ===")
    print("Corrigiendo códigos que empiezan con 0 -> Q")
    
    # 1. Procesar archivo manual
    print("\n1. Procesando archivo de texto...")
    enfermedades = procesar_archivo_manual(archivo_txt)
    
    if not enfermedades:
        print("❌ No se pudieron extraer enfermedades del archivo")
        return
    
    # 2. Generar reporte de correcciones
    print("\n2. Generando reporte de correcciones...")
    reporte = generar_reporte_correcciones(enfermedades)
    
    print(f"📊 ESTADÍSTICAS:")
    print(f"   Total de enfermedades: {reporte['total_enfermedades']}")
    print(f"   Correcciones 0→Q realizadas: {reporte['correcciones_0_a_q']}")
    print(f"   Códigos CIE-10 válidos: {reporte['codigos_validos']}")
    print(f"   Enfermedades sin código: {reporte['sin_codigo']}")
    print(f"   Códigos únicos: {reporte['codigos_unicos']}")
    
    # Mostrar distribución por categorías
    print(f"\n📈 DISTRIBUCIÓN POR CATEGORÍAS:")
    categorias_ordenadas = sorted(reporte['categorias'].items(), key=lambda x: x[1], reverse=True)
    for letra, count in categorias_ordenadas[:10]:
        print(f"   {letra}**: {count} códigos")
    
    # Mostrar ejemplos de correcciones
    if reporte['correcciones_0_a_q']:
        print(f"\n🔧 EJEMPLOS DE CORRECCIONES (0→Q):")
        for i, correccion in enumerate(reporte['lista_correcciones'][:10]):
            print(f"   {i+1}. {correccion['codigo_original']} → {correccion['codigo_cie10']}: {correccion['nombre'][:50]}...")
    
    # 3. Generar CSV
    print(f"\n3. Generando archivo CSV...")
    if generar_csv_corregido(enfermedades, archivo_csv):
        print(f"✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"📄 Archivo generado: {archivo_csv}")
        
        # Guardar reporte detallado
        archivo_reporte = archivo_csv.replace('.csv', '_reporte.txt')
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE CORRECCIONES - ENFERMEDADES RARAS COLOMBIA 2023\n")
            f.write("="*60 + "\n\n")
            f.write(f"Archivo fuente: {archivo_txt}\n")
            f.write(f"Archivo generado: {archivo_csv}\n")
            f.write(f"Total de enfermedades: {reporte['total_enfermedades']}\n")
            f.write(f"Correcciones 0→Q: {reporte['correcciones_0_a_q']}\n")
            f.write(f"Códigos válidos: {reporte['codigos_validos']}\n")
            f.write(f"Sin código: {reporte['sin_codigo']}\n")
            f.write(f"Códigos únicos: {reporte['codigos_unicos']}\n\n")
            
            f.write("CORRECCIONES REALIZADAS (0→Q):\n")
            f.write("-" * 40 + "\n")
            for correccion in reporte['lista_correcciones']:
                f.write(f"{correccion['codigo_original']} → {correccion['codigo_cie10']}: {correccion['nombre']}\n")
            
            f.write("\nDISTRIBUCIÓN POR CATEGORÍAS:\n")
            f.write("-" * 40 + "\n")
            for letra, count in categorias_ordenadas:
                f.write(f"{letra}**: {count} códigos\n")
        
        print(f"📋 Reporte guardado: {archivo_reporte}")
        
    else:
        print("❌ Error al generar archivo CSV")

if __name__ == "__main__":
    main()
