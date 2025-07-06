#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INICIADOR DE HOMOLOGACIÓN MASIVA
Versión simplificada para comenzar el procesamiento por lotes

Ejecuta homologación de las 2,249 enfermedades colombianas
en lotes manejables con control de progreso
"""

import os
import sys

def main():
    print("=" * 80)
    print("🚀 INICIADOR DE HOMOLOGACIÓN MASIVA COLOMBIA ↔ ORPHANET")
    print("=" * 80)
    
    print("📊 CONFIGURACIÓN PROPUESTA:")
    print("📋 Total enfermedades: 2,249")
    print("📦 Tamaño de lote: 150 enfermedades")
    print("🎯 Total lotes: ~15 lotes")
    print("⏱️  Delay entre requests: 1.2 segundos")
    print("🕐 Tiempo estimado total: ~75 minutos")
    print("💾 Auto-guardado cada lote")
    
    print(f"\n📋 OPCIONES DE EJECUCIÓN:")
    print(f"1. 🧪 PRUEBA PEQUEÑA (1 lote = 150 enfermedades)")
    print(f"2. 📊 EJECUCIÓN PARCIAL (5 lotes = 750 enfermedades)")
    print(f"3. 🚀 EJECUCIÓN COMPLETA (15 lotes = 2,249 enfermedades)")
    print(f"4. ⚙️  CONFIGURACIÓN PERSONALIZADA")
    
    while True:
        opcion = input(f"\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            print(f"\n🧪 EJECUTANDO PRUEBA PEQUEÑA...")
            comando = 'python homologacion_masiva_lotes.py --max-lotes 1'
            break
        elif opcion == "2":
            print(f"\n📊 EJECUTANDO EJECUCIÓN PARCIAL...")
            comando = 'python homologacion_masiva_lotes.py --max-lotes 5'
            break
        elif opcion == "3":
            print(f"\n🚀 EJECUTANDO HOMOLOGACIÓN COMPLETA...")
            comando = 'python homologacion_masiva_lotes.py'
            break
        elif opcion == "4":
            print(f"\n⚙️  CONFIGURACIÓN PERSONALIZADA:")
            try:
                lotes = int(input("Número de lotes a procesar: "))
                tamano = int(input("Tamaño de lote (recomendado 150): ") or "150")
                delay = float(input("Delay entre requests en segundos (recomendado 1.2): ") or "1.2")
                
                comando = f'python homologacion_masiva_lotes.py --max-lotes {lotes} --lote {tamano} --delay {delay}'
                print(f"\n⚙️  Configuración personalizada aplicada")
                break
            except ValueError:
                print("❌ Valores inválidos, intenta de nuevo")
                continue
        else:
            print("❌ Opción inválida, selecciona 1-4")
            continue
    
    print(f"\n📋 INFORMACIÓN IMPORTANTE:")
    print(f"✅ Los resultados se guardan automáticamente en cada lote")
    print(f"🔄 Puedes interrumpir con Ctrl+C y reanudar después")
    print(f"📁 Resultados se guardan en carpeta: resultados_homologacion/")
    print(f"📊 El progreso se guarda en: progreso_homologacion.json")
    
    print(f"\n🎯 COMANDO A EJECUTAR:")
    print(f"   {comando}")
    
    confirmar = input(f"\n¿Ejecutar homologación? (s/N): ").strip().lower()
    
    if confirmar in ['s', 'si', 'sí', 'y', 'yes']:
        print(f"\n🚀 INICIANDO HOMOLOGACIÓN...")
        print(f"=" * 80)
        
        # Ejecutar el comando
        os.system(comando)
        
    else:
        print(f"❌ Operación cancelada")
        print(f"\nPara ejecutar manualmente:")
        print(f"   {comando}")

if __name__ == "__main__":
    main()
