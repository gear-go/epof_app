#!/usr/bin/env python3
"""
Generador de reporte de homologación mejorado
Convierte los resultados de la homologación directa al formato esperado
"""

import pandas as pd
from datetime import datetime
import sys

def convertir_a_formato_esperado(archivo_homologacion):
    """
    Convierte el archivo de homologación al formato esperado similar a homologacion_orphanet_escalable
    """
    print(f"🔄 Procesando archivo: {archivo_homologacion}")
    
    try:
        df = pd.read_csv(archivo_homologacion, encoding='utf-8')
        print(f"📊 Total de registros: {len(df)}")
        
        # Filtrar solo las coincidencias encontradas
        df_encontrados = df[df['encontrado'] == True].copy()
        print(f"✅ Coincidencias encontradas: {len(df_encontrados)}")
        
        # Crear el formato de salida esperado
        df_salida = pd.DataFrame()
        
        # Mapear las columnas al formato esperado
        df_salida['ORPHA_Number'] = df_encontrados['orpha_number']
        df_salida['ORPHA_URL'] = df_encontrados['orpha_number'].apply(
            lambda x: f"https://www.orpha.net/es/disease/detail/{x}" if pd.notna(x) and x != '' else ''
        )
        df_salida['Nombre_Orphanet'] = df_encontrados['nombre_orphanet']
        df_salida['CIE10_Orphanet'] = df_encontrados['codigos_cie10_orphanet']
        df_salida['Numero_Colombia'] = df_encontrados['numero_colombia']
        df_salida['Nombre_Colombia'] = df_encontrados['nombre_colombia']
        df_salida['CIE10_Colombia'] = df_encontrados['codigo_cie10_formateado']
        
        # Clasificar tipo de match basado en similitud
        def clasificar_match(similitud):
            if similitud == 100:
                return 'nombre_exacto'
            elif similitud >= 85:
                return 'nombre_muy_similar'
            elif similitud >= 70:
                return 'nombre_similar'
            else:
                return 'nombre_parcial'
        
        df_salida['Tipo_Match'] = df_encontrados['similitud'].apply(clasificar_match)
        df_salida['Similitud'] = df_encontrados['similitud'] / 100  # Convertir a decimal
        df_salida['Observaciones_Colombia'] = df_encontrados['observaciones_colombia']
        
        # Ordenar por similitud descendente
        df_salida = df_salida.sort_values(['Similitud'], ascending=False)
        
        return df_salida
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return None

def generar_estadisticas(df_original, df_convertido):
    """Genera estadísticas comparativas"""
    stats = {
        'total_colombia': len(df_original),
        'total_coincidencias': len(df_convertido),
        'tasa_exito': (len(df_convertido) / len(df_original)) * 100,
        'matches_exactos': len(df_convertido[df_convertido['Tipo_Match'] == 'nombre_exacto']),
        'matches_muy_similares': len(df_convertido[df_convertido['Tipo_Match'] == 'nombre_muy_similar']),
        'matches_similares': len(df_convertido[df_convertido['Tipo_Match'] == 'nombre_similar']),
        'matches_parciales': len(df_convertido[df_convertido['Tipo_Match'] == 'nombre_parcial'])
    }
    return stats

def main():
    # Archivo de entrada (el más reciente)
    archivo_entrada = 'homologacion_orphanet_directa_20250702_074955.csv'
    
    print("🚀 GENERADOR DE REPORTE DE HOMOLOGACIÓN")
    print("=" * 55)
    
    # Leer archivo original para estadísticas
    try:
        df_original = pd.read_csv(archivo_entrada, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {archivo_entrada}")
        print("📋 Archivos disponibles:")
        import glob
        archivos = glob.glob('homologacion_orphanet_directa_*.csv')
        for archivo in archivos:
            print(f"   • {archivo}")
        sys.exit(1)
    
    # Convertir al formato esperado
    df_convertido = convertir_a_formato_esperado(archivo_entrada)
    
    if df_convertido is None:
        sys.exit(1)
    
    # Generar nombre de archivo de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = f'homologacion_orphanet_final_{timestamp}.csv'
    
    # Guardar resultado
    df_convertido.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    # Generar estadísticas
    stats = generar_estadisticas(df_original, df_convertido)
    
    print("=" * 55)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 55)
    print(f"📈 Total enfermedades Colombia: {stats['total_colombia']}")
    print(f"✅ Total coincidencias encontradas: {stats['total_coincidencias']}")
    print(f"🎯 Tasa de éxito: {stats['tasa_exito']:.1f}%")
    print(f"")
    print(f"Por tipo de coincidencia:")
    print(f"   • Exactas (100%): {stats['matches_exactos']}")
    print(f"   • Muy similares (85-99%): {stats['matches_muy_similares']}")
    print(f"   • Similares (70-84%): {stats['matches_similares']}")
    print(f"   • Parciales (60-69%): {stats['matches_parciales']}")
    print(f"")
    print(f"📁 Archivo generado: {archivo_salida}")
    
    # Generar archivo de reporte de texto
    archivo_reporte = f'reporte_homologacion_{timestamp}.md'
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("# REPORTE DE HOMOLOGACIÓN ORPHANET - COLOMBIA\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Archivo fuente:** {archivo_entrada}\n")
        f.write(f"**Archivo resultado:** {archivo_salida}\n\n")
        f.write("## Resumen Ejecutivo\n\n")
        f.write(f"Se procesaron **{stats['total_colombia']} enfermedades raras** del listado oficial de Colombia 2023, ")
        f.write(f"logrando encontrar coincidencias para **{stats['total_coincidencias']} enfermedades** ")
        f.write(f"(**{stats['tasa_exito']:.1f}% de éxito**).\n\n")
        
        f.write("## Distribución por Tipo de Coincidencia\n\n")
        f.write(f"- **Coincidencias exactas (100%):** {stats['matches_exactos']} enfermedades\n")
        f.write(f"- **Coincidencias muy similares (85-99%):** {stats['matches_muy_similares']} enfermedades\n")
        f.write(f"- **Coincidencias similares (70-84%):** {stats['matches_similares']} enfermedades\n")
        f.write(f"- **Coincidencias parciales (60-69%):** {stats['matches_parciales']} enfermedades\n\n")
        
        f.write("## Top 20 Mejores Coincidencias\n\n")
        top_20 = df_convertido.head(20)
        f.write("| Similitud | Nombre Colombia | Nombre Orphanet | ORPHA |\n")
        f.write("|-----------|-----------------|-----------------|-------|\n")
        for _, row in top_20.iterrows():
            similitud = f"{row['Similitud']*100:.1f}%"
            nombre_col = row['Nombre_Colombia'][:50] + "..." if len(row['Nombre_Colombia']) > 50 else row['Nombre_Colombia']
            nombre_orpha = row['Nombre_Orphanet'][:50] + "..." if len(row['Nombre_Orphanet']) > 50 else row['Nombre_Orphanet']
            orpha_num = row['ORPHA_Number']
            f.write(f"| {similitud} | {nombre_col} | {nombre_orpha} | {orpha_num} |\n")
    
    print(f"📄 Reporte detallado: {archivo_reporte}")
    print("=" * 55)
    print("✅ Proceso completado exitosamente")

if __name__ == '__main__':
    main()
