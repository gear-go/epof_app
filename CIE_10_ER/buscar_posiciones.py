#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUSCADOR DE POSICIONES - Encuentra enfermedades específicas en el CSV
"""

import pandas as pd

def buscar_posiciones():
    df = pd.read_csv('enfermedades_raras_colombia_2023_corregido.csv')
    
    nombres_test = ['Acondroplasia', 'Acidemia isovalérica', 'Acromegalia', 'Albinismo', 'Síndrome de Aicardi']
    
    print("POSICIONES DE ENFERMEDADES CONOCIDAS:")
    print("=" * 50)
    
    for nombre in nombres_test:
        indices = df[df['Nombre_Enfermedad'].str.contains(nombre, case=False, na=False)].index
        if len(indices) > 0:
            for idx in indices:
                fila = idx + 2  # +2 porque empieza en 1 y el header
                print(f"Fila {fila}: {df.iloc[idx]['Nombre_Enfermedad']} ({df.iloc[idx]['Código_CIE10']})")
        else:
            print(f"No encontrado: {nombre}")
    
    print("\nRECOMENDACIÓN:")
    print("Probar homologación en el rango 151-300 para encontrar estas enfermedades")

if __name__ == "__main__":
    buscar_posiciones()
