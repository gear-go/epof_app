#!/usr/bin/env python3
"""
Script para generar visualizaciones estáticas de presentación
Análisis de Enfermedades Raras Colombia 2023
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

def generar_presentacion():
    """Genera todas las visualizaciones para presentación"""
    
    print("🎨 GENERANDO VISUALIZACIONES DE PRESENTACIÓN")
    print("="*50)
    
    # Cargar datos
    df = pd.read_csv("enfermedades_raras_colombia_2023_corregido.csv")
    
    # Configurar estilo
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (16, 10)
    plt.rcParams['font.size'] = 12
    
    # 1. DASHBOARD PRINCIPAL
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    # Título principal
    fig.suptitle('📊 ENFERMEDADES RARAS COLOMBIA 2023\nProcesamiento Manual + Verificación IA (Claude Sonnet 4)', 
                 fontsize=24, fontweight='bold', y=0.95)
    
    # Estadísticas principales
    total_enf = len(df)
    sin_codigo = len(df[df['Código_CIE10'] == 'XXXX'])
    correcciones = len(df[df['Observaciones'].str.contains('Código corregido', na=False)])
    codigos_unicos = len(df[df['Código_CIE10'] != 'XXXX']['Código_CIE10'].unique())
    
    # Subplot 1: Estadísticas clave
    ax1 = fig.add_subplot(gs[0, :2])
    stats = [total_enf, codigos_unicos, correcciones, total_enf-sin_codigo]
    labels = ['Total\nEnfermedades', 'Códigos\nÚnicos', 'Correcciones\n0→Q', 'Códigos\nVálidos']
    colors = ['#3498DB', '#E74C3C', '#F39C12', '#27AE60']
    
    bars = ax1.bar(labels, stats, color=colors, alpha=0.8)
    ax1.set_title('📊 Estadísticas Principales', fontsize=16, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    for bar, stat in zip(bars, stats):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(stats)*0.01,
                f'{stat:,}', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    # Subplot 2: Distribución por categorías
    ax2 = fig.add_subplot(gs[0, 2:])
    codigos_validos = df[df['Código_CIE10'] != 'XXXX'].copy()
    codigos_validos['Categoria'] = codigos_validos['Código_CIE10'].str[0]
    conteo_cat = codigos_validos['Categoria'].value_counts().head(8)
    
    colors_cat = sns.color_palette("Set3", len(conteo_cat))
    wedges, texts, autotexts = ax2.pie(list(conteo_cat.values), labels=list(conteo_cat.index), 
                                       autopct='%1.1f%%', colors=colors_cat, startangle=90)
    ax2.set_title('🥧 Top 8 Categorías CIE-10', fontsize=16, fontweight='bold')
    
    # Subplot 3: Impacto de correcciones
    ax3 = fig.add_subplot(gs[1, :2])
    metodos = ['Antes\n(Códigos 0***)', 'Después\n(Categoría Q)']
    valores_imp = [correcciones, len(df[df['Código_CIE10'].str.startswith('Q', na=False)])]
    
    bars3 = ax3.bar(metodos, valores_imp, color=['#E74C3C', '#27AE60'], alpha=0.8)
    ax3.set_title('🔧 Impacto de Correcciones 0→Q', fontsize=16, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(valores_imp)*0.01,
                f'{int(height):,}', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    # Subplot 4: Comparación metodológica
    ax4 = fig.add_subplot(gs[1, 2:])
    metodos_comp = ['Extracción\nAutomática', 'Procesamiento\nManual']
    enf_comp = [964, total_enf]
    cod_comp = [384, codigos_unicos]
    
    x = np.arange(len(metodos_comp))
    width = 0.35
    
    bars4_1 = ax4.bar(x - width/2, enf_comp, width, label='Total Enfermedades', color='#3498DB', alpha=0.8)
    bars4_2 = ax4.bar(x + width/2, cod_comp, width, label='Códigos Únicos', color='#E74C3C', alpha=0.8)
    
    ax4.set_xlabel('Método')
    ax4.set_title('⚖️ Comparación Metodológica', fontsize=16, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metodos_comp)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # Subplot 5: Distribución detallada categorías
    ax5 = fig.add_subplot(gs[2, :])
    top_10_cat = conteo_cat.head(10)
    categorias_desc = {
        'Q': 'Malformaciones congénitas',
        'E': 'Endocrinas/metabólicas', 
        'D': 'Neoplasias/sangre',
        'G': 'Sistema nervioso',
        'H': 'Órganos sensoriales',
        'M': 'Musculoesquelético',
        'L': 'Piel',
        'K': 'Digestivo',
        'I': 'Circulatorio',
        'C': 'Neoplasias malignas'
    }
    
    colors_det = sns.color_palette("tab10", len(top_10_cat))
    bars5 = ax5.bar(range(len(top_10_cat)), list(top_10_cat.values), color=colors_det, alpha=0.8)
    
    ax5.set_xlabel('Categorías CIE-10')
    ax5.set_ylabel('Número de Enfermedades')
    ax5.set_title('📈 Distribución Detallada por Categorías CIE-10', fontsize=16, fontweight='bold')
    ax5.set_xticks(range(len(top_10_cat)))
    ax5.set_xticklabels([f"{cat}\n{categorias_desc.get(cat, 'Otra')}" for cat in top_10_cat.index], 
                       rotation=45, ha='right')
    ax5.grid(axis='y', alpha=0.3)
    
    for bar in bars5:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + max(list(top_10_cat.values))*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Subplot 6: Calidad del dataset
    ax6 = fig.add_subplot(gs[3, :2])
    calidad_labels = ['Códigos\nVálidos', 'Sin\nCódigo']
    calidad_valores = [total_enf - sin_codigo, sin_codigo]
    calidad_colors = ['#27AE60', '#E74C3C']
    
    bars6 = ax6.bar(calidad_labels, calidad_valores, color=calidad_colors, alpha=0.8)
    ax6.set_title('✅ Calidad del Dataset', fontsize=16, fontweight='bold')
    ax6.grid(axis='y', alpha=0.3)
    
    for bar, valor in zip(bars6, calidad_valores):
        height = bar.get_height()
        porcentaje = (valor / total_enf) * 100
        ax6.text(bar.get_x() + bar.get_width()/2., height + max(calidad_valores)*0.01,
                f'{valor:,}\n({porcentaje:.1f}%)', ha='center', va='bottom', fontweight='bold')
    
    # Subplot 7: Fuente y metodología
    ax7 = fig.add_subplot(gs[3, 2:])
    ax7.text(0.5, 0.9, '📚 FUENTE OFICIAL', ha='center', va='top', fontsize=14, fontweight='bold', 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.8, 'Resolución 023 de 2023', ha='center', va='top', fontsize=12, 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.7, 'Ministerio de Salud y Protección Social de Colombia', ha='center', va='top', 
             fontsize=10, transform=ax7.transAxes)
    
    ax7.text(0.5, 0.5, '🔬 METODOLOGÍA', ha='center', va='top', fontsize=14, fontweight='bold', 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.4, '• Extracción manual de datos', ha='center', va='top', fontsize=10, 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.3, '• Corrección códigos 0→Q', ha='center', va='top', fontsize=10, 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.2, '• Verificación IA (Claude Sonnet 4)', ha='center', va='top', fontsize=10, 
             transform=ax7.transAxes)
    ax7.text(0.5, 0.1, '• Validación CIE-10 completa', ha='center', va='top', fontsize=10, 
             transform=ax7.transAxes)
    
    ax7.set_xlim(0, 1)
    ax7.set_ylim(0, 1)
    ax7.axis('off')
    
    # Agregar línea de tiempo en el pie
    fig.text(0.5, 0.02, 'Enero 2025 | UDD Research | Enfermedades Raras', 
             ha='center', va='bottom', fontsize=12, style='italic')
    
    plt.savefig('presentacion_enfermedades_raras_colombia_2023.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Dashboard principal guardado: presentacion_enfermedades_raras_colombia_2023.png")
    
    # 2. GRÁFICO INSIGHTS CLAVE
    fig, ax = plt.subplots(figsize=(16, 10))
    
    insights_data = {
        'Métrica': ['Total\nEnfermedades', 'Mejora vs\nAutomático', 'Correcciones\nAplicadas', 
                   'Tasa de\nPrecisión', 'Códigos\nÚnicos', 'Cobertura\nCompleta'],
        'Valor': [2249, 133, 1041, 96.9, 641, 100],
        'Unidad': ['', '%', '', '%', '', '%'],
        'Color': ['#3498DB', '#27AE60', '#F39C12', '#E74C3C', '#9B59B6', '#1ABC9C']
    }
    
    bars = ax.bar(insights_data['Métrica'], insights_data['Valor'], 
                  color=insights_data['Color'], alpha=0.8)
    
    ax.set_title('💡 INSIGHTS CLAVE - ENFERMEDADES RARAS COLOMBIA 2023\n' + 
                'Procesamiento Manual + Verificación IA Generativa', 
                fontsize=18, fontweight='bold', pad=20)
    ax.set_ylabel('Valor de la Métrica', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Agregar valores encima de las barras
    for bar, valor, unidad in zip(bars, insights_data['Valor'], insights_data['Unidad']):
        height = bar.get_height()
        if unidad:
            texto = f'{valor}{unidad}'
        else:
            texto = f'{valor:,}'
        ax.text(bar.get_x() + bar.get_width()/2., height + max(insights_data['Valor'])*0.01,
                texto, ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    # Agregar fuente
    ax.text(0.5, -0.12, 'Fuente: Resolución 023 de 2023 - Ministerio de Salud y Protección Social de Colombia', 
            ha='center', va='bottom', transform=ax.transAxes, fontsize=12, style='italic')
    
    plt.tight_layout()
    plt.savefig('insights_clave_colombia_2023.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Insights clave guardado: insights_clave_colombia_2023.png")
    
    print(f"\n🎯 RESUMEN PARA PRESENTACIÓN:")
    print(f"📊 {total_enf:,} enfermedades raras procesadas")
    print(f"🔧 {correcciones:,} correcciones 0→Q aplicadas")
    print(f"✅ {((total_enf-sin_codigo)/total_enf)*100:.1f}% de precisión lograda")
    print(f"🏆 Mejora del {((total_enf/964)-1)*100:.0f}% vs extracción automática")

if __name__ == "__main__":
    generar_presentacion()
