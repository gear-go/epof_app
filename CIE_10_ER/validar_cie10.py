#!/usr/bin/env python3
"""
Script para validar y limpiar los datos extraídos de códigos CIE-10
y generar un reporte de calidad detallado
"""

import pandas as pd
import re
from collections import Counter
import csv

def validar_codigo_cie10(codigo):
    """Valida formato de código CIE-10"""
    if not codigo or len(codigo) != 4:
        return False
    return bool(re.match(r'^[A-Z]\d{2}[\dX]$', codigo))

def limpiar_nombre_enfermedad(nombre):
    """Limpia y normaliza el nombre de la enfermedad"""
    if not nombre:
        return ""
    
    # Remover números de lista del inicio
    nombre = re.sub(r'^\d+\s*', '', nombre)
    
    # Limpiar espacios múltiples
    nombre = re.sub(r'\s+', ' ', nombre)
    
    # Remover caracteres especiales al final
    nombre = nombre.strip('.,;:-')
    
    return nombre.strip()

def generar_reporte_calidad(archivo_csv):
    """Genera un reporte detallado de control de calidad"""
    
    print("=== REPORTE DE CONTROL DE CALIDAD ===\n")
    
    # Leer datos
    df = pd.read_csv(archivo_csv)
    
    # Estadísticas básicas
    total_registros = len(df)
    print(f"📊 ESTADÍSTICAS BÁSICAS:")
    print(f"   Total de registros: {total_registros}")
    
    # Validar códigos CIE-10
    codigos_validos = df[df['Código_CIE10'].apply(validar_codigo_cie10)]
    codigos_invalidos = df[~df['Código_CIE10'].apply(validar_codigo_cie10)]
    
    print(f"   Códigos CIE-10 válidos: {len(codigos_validos)}")
    print(f"   Códigos CIE-10 inválidos: {len(codigos_invalidos)}")
    
    # Códigos únicos
    codigos_unicos = df[df['Código_CIE10'] != 'XXXX']['Código_CIE10'].nunique()
    print(f"   Códigos únicos (sin XXXX): {codigos_unicos}")
    
    # Enfermedades sin código
    sin_codigo = len(df[df['Código_CIE10'] == 'XXXX'])
    print(f"   Enfermedades sin código: {sin_codigo}")
    
    # Duplicados por código
    duplicados_codigo = df[df['Código_CIE10'] != 'XXXX'].groupby('Código_CIE10').size()
    codigos_duplicados = duplicados_codigo[duplicados_codigo > 1]
    
    print(f"\n🔍 ANÁLISIS DE DUPLICADOS:")
    print(f"   Códigos que aparecen múltiples veces: {len(codigos_duplicados)}")
    
    if len(codigos_duplicados) > 0:
        print(f"   Top 10 códigos más repetidos:")
        for codigo, count in codigos_duplicados.head(10).items():
            print(f"     {codigo}: {count} veces")
    
    # Distribución por categorías CIE-10
    print(f"\n📈 DISTRIBUCIÓN POR CATEGORÍAS CIE-10:")
    categorias = df[df['Código_CIE10'] != 'XXXX']['Código_CIE10'].str[0].value_counts()
    for letra, count in categorias.head(10).items():
        print(f"   {letra}**: {count} códigos")
    
    # Verificar formato de nombres
    print(f"\n📝 ANÁLISIS DE NOMBRES:")
    nombres_vacios = len(df[df['Nombre_Enfermedad'].str.strip() == ''])
    nombres_cortos = len(df[df['Nombre_Enfermedad'].str.len() < 5])
    nombres_con_numeros = len(df[df['Nombre_Enfermedad'].str.match(r'^\d+')])
    
    print(f"   Nombres vacíos: {nombres_vacios}")
    print(f"   Nombres muy cortos (<5 caracteres): {nombres_cortos}")
    print(f"   Nombres que empiezan con número: {nombres_con_numeros}")
    
    # Códigos inválidos detallados
    if len(codigos_invalidos) > 0:
        print(f"\n❌ CÓDIGOS INVÁLIDOS ENCONTRADOS:")
        count = 0
        for idx, row in codigos_invalidos.head(10).iterrows():
            count += 1
            print(f"   Registro {count}: '{row['Código_CIE10']}' - {row['Nombre_Enfermedad'][:50]}...")
    
    # Generar archivo limpio
    print(f"\n🧹 GENERANDO ARCHIVO LIMPIO...")
    
    # Crear DataFrame limpio
    df_limpio = df.copy()
    
    # Limpiar nombres
    df_limpio['Nombre_Enfermedad'] = df_limpio['Nombre_Enfermedad'].apply(limpiar_nombre_enfermedad)
    
    # Marcar códigos inválidos como XXXX
    df_limpio.loc[~df_limpio['Código_CIE10'].apply(validar_codigo_cie10), 'Código_CIE10'] = 'XXXX'
    df_limpio.loc[~df_limpio['Código_CIE10'].apply(validar_codigo_cie10), 'Observaciones'] = 'Código inválido corregido'
    
    # Filtrar registros con nombres muy cortos o vacíos
    df_limpio = df_limpio[df_limpio['Nombre_Enfermedad'].str.len() >= 5]
    
    # Renumerar
    df_limpio['Número'] = range(1, len(df_limpio) + 1)
    
    # Guardar archivo limpio
    archivo_limpio = archivo_csv.replace('.csv', '_limpio.csv')
    df_limpio.to_csv(archivo_limpio, index=False, encoding='utf-8')
    
    print(f"   Archivo limpio generado: {archivo_limpio}")
    print(f"   Registros en archivo limpio: {len(df_limpio)}")
    
    # Generar reporte detallado
    archivo_reporte = archivo_csv.replace('.csv', '_reporte.txt')
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("REPORTE DETALLADO DE EXTRACCIÓN CIE-10\n")
        f.write("="*50 + "\n\n")
        f.write(f"Archivo original: {archivo_csv}\n")
        f.write(f"Total registros originales: {total_registros}\n")
        f.write(f"Total registros limpios: {len(df_limpio)}\n")
        f.write(f"Códigos CIE-10 válidos: {len(codigos_validos)}\n")
        f.write(f"Códigos únicos: {codigos_unicos}\n")
        f.write(f"Enfermedades sin código: {sin_codigo}\n\n")
        
        f.write("CÓDIGOS MÁS FRECUENTES:\n")
        f.write("-" * 30 + "\n")
        for codigo, count in duplicados_codigo.head(20).items():
            f.write(f"{codigo}: {count} veces\n")
        
        f.write("\nDISTRIBUCIÓN POR CATEGORÍAS:\n")
        f.write("-" * 30 + "\n")
        for letra, count in categorias.items():
            categoria_desc = obtener_descripcion_categoria(letra)
            f.write(f"{letra}** ({categoria_desc}): {count} códigos\n")
        
        if len(codigos_invalidos) > 0:
            f.write("\nCÓDIGOS INVÁLIDOS:\n")
            f.write("-" * 30 + "\n")
            count = 0
            for idx, row in codigos_invalidos.iterrows():
                count += 1
                f.write(f"Registro {count}: '{row['Código_CIE10']}' - {row['Nombre_Enfermedad']}\n")
    
    print(f"   Reporte detallado generado: {archivo_reporte}")
    
    return {
        'total_original': total_registros,
        'total_limpio': len(df_limpio),
        'codigos_validos': len(codigos_validos),
        'codigos_unicos': codigos_unicos,
        'sin_codigo': sin_codigo
    }

def obtener_descripcion_categoria(letra):
    """Obtiene descripción de categoría CIE-10"""
    categorias = {
        'A': 'Enfermedades infecciosas y parasitarias',
        'B': 'Enfermedades infecciosas y parasitarias',
        'C': 'Neoplasias malignas',
        'D': 'Neoplasias benignas y sangre',
        'E': 'Enfermedades endocrinas y metabólicas',
        'F': 'Trastornos mentales y del comportamiento',
        'G': 'Enfermedades del sistema nervioso',
        'H': 'Enfermedades de órganos sensoriales',
        'I': 'Enfermedades del sistema circulatorio',
        'J': 'Enfermedades del sistema respiratorio',
        'K': 'Enfermedades del sistema digestivo',
        'L': 'Enfermedades de la piel',
        'M': 'Enfermedades del sistema musculoesquelético',
        'N': 'Enfermedades del sistema genitourinario',
        'O': 'Embarazo, parto y puerperio',
        'P': 'Afecciones del período perinatal',
        'Q': 'Malformaciones congénitas',
        'R': 'Síntomas y signos anormales',
        'S': 'Traumatismos y envenenamientos',
        'T': 'Traumatismos y envenenamientos',
        'V': 'Causas externas',
        'W': 'Causas externas',
        'X': 'Causas externas',
        'Y': 'Causas externas',
        'Z': 'Factores que influyen en el estado de salud'
    }
    return categorias.get(letra, 'Categoría desconocida')

def main():
    archivo_csv = "enfermedades_raras_cie10.csv"
    
    try:
        resultado = generar_reporte_calidad(archivo_csv)
        print(f"\n✅ PROCESO COMPLETADO")
        print(f"   Registros procesados: {resultado['total_original']}")
        print(f"   Registros válidos: {resultado['total_limpio']}")
        print(f"   Tasa de éxito: {(resultado['total_limpio']/resultado['total_original']*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
