#!/usr/bin/env python3
"""
Análisis de enfermedades únicas y grupos en la homologación Orphanet-Colombia
Genera estadísticas y visualizaciones de los datos homologados
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

def cargar_y_analizar_datos(archivo_csv):
    """
    Carga el archivo CSV y realiza análisis de enfermedades únicas
    """
    print(f"🔄 Cargando archivo: {archivo_csv}")
    
    try:
        df = pd.read_csv(archivo_csv)
        print(f"📊 Total de registros: {len(df)}")
        
        # Información básica
        print("\n" + "=" * 60)
        print("📋 INFORMACIÓN BÁSICA DEL DATASET")
        print("=" * 60)
        print(f"Total de registros: {len(df)}")
        print(f"Columnas: {df.columns.tolist()}")
        
        # Verificar duplicados por ORPHA_Number
        orphas_unicos = df['ORPHA_Number'].nunique()
        orphas_duplicados = len(df) - orphas_unicos
        
        print(f"\n🔍 ANÁLISIS DE UNICIDAD:")
        print(f"Números ORPHA únicos: {orphas_unicos}")
        print(f"Registros duplicados: {orphas_duplicados}")
        
        if orphas_duplicados > 0:
            print("\n⚠️  DUPLICADOS ENCONTRADOS:")
            duplicados = df[df.duplicated(subset=['ORPHA_Number'], keep=False)].sort_values('ORPHA_Number')
            for orpha in duplicados['ORPHA_Number'].unique():
                casos = duplicados[duplicados['ORPHA_Number'] == orpha]
                print(f"  ORPHA:{orpha} aparece {len(casos)} veces:")
                for _, caso in casos.iterrows():
                    print(f"    - {caso['Nombre_Colombia']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return None

def clasificar_enfermedades_por_grupos(df):
    """
    Clasifica las enfermedades por grupos basándose en patrones en los nombres
    """
    print("\n" + "=" * 60)
    print("🏷️  CLASIFICACIÓN POR GRUPOS DE ENFERMEDADES")
    print("=" * 60)
    
    # Definir patrones para clasificar enfermedades
    patrones_grupos = {
        'Acidemias/Acidurias': [
            r'acidemia', r'aciduria', r'ácido', r'metilmalónic', r'propiónic', 
            r'isovaléric', r'glutáric', r'malónic'
        ],
        'Deficiencias Enzimáticas': [
            r'deficiencia', r'déficit', r'deficiency', r'ausencia.*enzim'
        ],
        'Síndromes': [
            r'síndrome', r'sindrome', r'syndrome'
        ],
        'Distrofias': [
            r'distrofia', r'dystrophy', r'distrofic'
        ],
        'Displasias': [
            r'displasia', r'dysplasia', r'displásic'
        ],
        'Anemias': [
            r'anemia', r'anémic', r'talasemia'
        ],
        'Neuropatías': [
            r'neuropatía', r'neuropathy', r'neural'
        ],
        'Miopatías': [
            r'miopatía', r'myopathy', r'muscular'
        ],
        'Ataxias': [
            r'ataxia', r'atáxic'
        ],
        'Leucodistrofias': [
            r'leucodistrofia', r'leukodystrophy'
        ],
        'Mucopolisacaridosis': [
            r'mucopolisacaridosis', r'mucopolysaccharidosis', r'MPS'
        ],
        'Lisosomales': [
            r'lisosomal', r'lysosomal', r'almacenamiento'
        ],
        'Malformaciones': [
            r'malformación', r'malformation', r'anomalía congénita'
        ],
        'Tumores Raros': [
            r'tumor', r'carcinoma', r'sarcoma', r'blastoma', r'neoplasia'
        ],
        'Inmunodeficiencias': [
            r'inmunodeficiencia', r'immunodeficiency', r'inmune'
        ]
    }
    
    # Clasificar cada enfermedad
    grupos = []
    
    for _, row in df.iterrows():
        nombre_orphanet = str(row['Nombre_Orphanet']).lower()
        nombre_colombia = str(row['Nombre_Colombia']).lower()
        texto_completo = f"{nombre_orphanet} {nombre_colombia}"
        
        grupo_encontrado = 'Otras Enfermedades Raras'
        
        for grupo, patrones in patrones_grupos.items():
            for patron in patrones:
                if re.search(patron, texto_completo):
                    grupo_encontrado = grupo
                    break
            if grupo_encontrado != 'Otras Enfermedades Raras':
                break
        
        grupos.append(grupo_encontrado)
    
    df['Grupo_Enfermedad'] = grupos
    
    # Contar por grupos
    contador_grupos = Counter(grupos)
    
    print(f"Total de grupos identificados: {len(contador_grupos)}")
    print("\nDistribución por grupos:")
    
    for i, (grupo, count) in enumerate(contador_grupos.most_common(), 1):
        porcentaje = (count / len(df)) * 100
        print(f"{i:2d}. {grupo}: {count} ({porcentaje:.1f}%)")
    
    return df, contador_grupos

def crear_visualizaciones(df, contador_grupos):
    """
    Crea visualizaciones de los datos
    """
    print("\n" + "=" * 60)
    print("📊 GENERANDO VISUALIZACIONES")
    print("=" * 60)
    
    # Configurar estilo
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Crear figura con subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis de Enfermedades Raras - Homologación Orphanet Colombia 2025', 
                 fontsize=16, fontweight='bold')
    
    # 1. Top 10 grupos más grandes
    top_10_grupos = dict(contador_grupos.most_common(10))
    
    ax1.barh(list(top_10_grupos.keys()), list(top_10_grupos.values()), 
             color=sns.color_palette("viridis", len(top_10_grupos)))
    ax1.set_title('Top 10 Grupos de Enfermedades Más Frecuentes', fontweight='bold')
    ax1.set_xlabel('Número de Enfermedades')
    
    # Agregar números en las barras
    for i, v in enumerate(top_10_grupos.values()):
        ax1.text(v + 1, i, str(v), va='center', fontweight='bold')
    
    # 2. Distribución de tipos de match
    tipo_match_counts = df['Tipo_Match'].value_counts()
    
    ax2.pie(tipo_match_counts.values, labels=tipo_match_counts.index, autopct='%1.1f%%',
            startangle=90)
    ax2.set_title('Distribución por Tipo de Coincidencia', fontweight='bold')
    
    # 3. Distribución de similitud
    ax3.hist(df['Similitud'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax3.set_title('Distribución de Similitud en la Homologación', fontweight='bold')
    ax3.set_xlabel('Similitud')
    ax3.set_ylabel('Frecuencia')
    ax3.axvline(df['Similitud'].mean(), color='red', linestyle='--', 
                label=f'Media: {df["Similitud"].mean():.2f}')
    ax3.legend()
    
    # 4. Top 10 códigos CIE-10 más frecuentes
    cie10_counts = df['CIE10_Colombia'].value_counts().head(10)
    
    ax4.bar(range(len(cie10_counts)), cie10_counts.values, 
            color=sns.color_palette("rocket", len(cie10_counts)))
    ax4.set_title('Top 10 Códigos CIE-10 Más Frecuentes', fontweight='bold')
    ax4.set_xlabel('Códigos CIE-10')
    ax4.set_ylabel('Frecuencia')
    ax4.set_xticks(range(len(cie10_counts)))
    ax4.set_xticklabels(cie10_counts.index, rotation=45, ha='right')
    
    # Agregar números en las barras
    for i, v in enumerate(cie10_counts.values):
        ax4.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar figura
    nombre_archivo = 'analisis_enfermedades_raras_colombia_2025.png'
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    print(f"📈 Gráfico guardado como: {nombre_archivo}")
    
    # Crear gráfico adicional solo para Top 10 grupos (más detallado)
    plt.figure(figsize=(12, 8))
    
    grupos_nombres = list(top_10_grupos.keys())
    grupos_valores = list(top_10_grupos.values())
    
    # Crear gradiente de colores
    colors = sns.color_palette("Set3", len(grupos_nombres))
    
    bars = plt.barh(grupos_nombres, grupos_valores, color=colors)
    
    plt.title('Top 10 Grupos de Enfermedades Raras en Colombia\n(Según Homologación con Orphanet 2025)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Número de Enfermedades', fontsize=12)
    plt.ylabel('Grupos de Enfermedades', fontsize=12)
    
    # Agregar números y porcentajes en las barras
    total = sum(grupos_valores)
    for i, (bar, valor) in enumerate(zip(bars, grupos_valores)):
        porcentaje = (valor / total) * 100
        plt.text(valor + max(grupos_valores) * 0.01, i, 
                f'{valor} ({porcentaje:.1f}%)', 
                va='center', ha='left', fontweight='bold', fontsize=10)
    
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    nombre_archivo_top10 = 'top_10_grupos_enfermedades_raras.png'
    plt.savefig(nombre_archivo_top10, dpi=300, bbox_inches='tight')
    print(f"📊 Gráfico Top 10 guardado como: {nombre_archivo_top10}")
    
    plt.show()

def generar_reporte_estadistico(df, contador_grupos):
    """
    Genera un reporte estadístico detallado
    """
    print("\n" + "=" * 60)
    print("📋 GENERANDO REPORTE ESTADÍSTICO")
    print("=" * 60)
    
    reporte = f"""
# REPORTE ESTADÍSTICO - ANÁLISIS DE ENFERMEDADES RARAS COLOMBIA 2025

## Resumen General
- **Total de enfermedades procesadas:** {len(df):,}
- **Números ORPHA únicos:** {df['ORPHA_Number'].nunique():,}
- **Grupos de enfermedades identificados:** {len(contador_grupos)}

## Estadísticas de Calidad
- **Similitud promedio:** {df['Similitud'].mean():.2f}
- **Similitud mediana:** {df['Similitud'].median():.2f}
- **Rango de similitud:** {df['Similitud'].min():.2f} - {df['Similitud'].max():.2f}

## Distribución por Tipo de Coincidencia
"""
    
    for tipo, count in df['Tipo_Match'].value_counts().items():
        porcentaje = (count / len(df)) * 100
        reporte += f"- **{tipo}:** {count} ({porcentaje:.1f}%)\n"
    
    reporte += f"\n## Top 15 Grupos de Enfermedades\n"
    
    for i, (grupo, count) in enumerate(contador_grupos.most_common(15), 1):
        porcentaje = (count / len(df)) * 100
        reporte += f"{i:2d}. **{grupo}:** {count} enfermedades ({porcentaje:.1f}%)\n"
    
    reporte += f"""
## Códigos CIE-10 Más Frecuentes
"""
    
    for codigo, count in df['CIE10_Colombia'].value_counts().head(10).items():
        reporte += f"- **{codigo}:** {count} casos\n"
    
    # Guardar reporte
    with open('reporte_analisis_enfermedades_raras.md', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("📄 Reporte guardado como: reporte_analisis_enfermedades_raras.md")

def main():
    archivo_csv = 'homologacion_orphanet_final_20250702_075313_con_orpha.csv'
    
    print("🚀 ANÁLISIS DE ENFERMEDADES ÚNICAS Y GRUPOS")
    print("=" * 60)
    
    # Cargar y analizar datos
    df = cargar_y_analizar_datos(archivo_csv)
    if df is None:
        return
    
    # Clasificar por grupos
    df, contador_grupos = clasificar_enfermedades_por_grupos(df)
    
    # Crear visualizaciones
    crear_visualizaciones(df, contador_grupos)
    
    # Generar reporte
    generar_reporte_estadistico(df, contador_grupos)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 60)
    print("Archivos generados:")
    print("📊 analisis_enfermedades_raras_colombia_2025.png")
    print("📈 top_10_grupos_enfermedades_raras.png")
    print("📄 reporte_analisis_enfermedades_raras.md")

if __name__ == '__main__':
    # Verificar dependencias
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("Instalando dependencias...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "seaborn"])
        import matplotlib.pyplot as plt
        import seaborn as sns
    
    main()
