#!/usr/bin/env python3
"""
Script para validar conectividad con Orphanet/Orphadata
Basado en: context_orphanet.md

Canales de acceso:
1. Ficheros "free products" (XML masivos)
2. API REST Orphadata (requiere token)
3. Endpoints SPARQL (ORDO/HOOM)

Autor: Análisis GRD Enfermedades Raras
Fecha: Julio 2025
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuración
TIMEOUT = 30
USER_AGENT = "OrphanetValidator/1.0 (Python/ValidacionColombia)"

def print_banner():
    """Imprime banner de inicio"""
    print("=" * 80)
    print("🔍 VALIDADOR DE CONECTIVIDAD ORPHANET")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("=" * 80)

def test_free_products():
    """
    Prueba acceso a ficheros "free products" (XML masivos)
    Basado en: context_orphanet.md sección 3
    """
    print("\n🔬 PRUEBA 1: Ficheros Free Products (XML masivos)")
    print("-" * 60)
    
    # Productos disponibles según documentación
    products = ["product1", "product3", "product4", "product6", "product7", "product9_prev", "product9_ages"]
    
    results = {}
    
    for product_id in products[:3]:  # Pruebamos los primeros 3 para no sobrecargar
        try:
            print(f"📦 Probando {product_id}...")
            
            # URL de metadatos
            meta_url = f"http://www.orphadata.org/cgi-bin/free_{product_id}_cross_xml.json"
            
            # Solicitud con timeout y headers
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(meta_url, timeout=TIMEOUT, headers=headers)
            
            if response.status_code == 200:
                try:
                    meta = response.json()
                    results[product_id] = {
                        "status": "✅ CONECTADO",
                        "fecha": meta.get("date", "N/A"),
                        "archivo": meta.get("product_file", "N/A"),
                        "size_mb": round(len(response.content) / 1024 / 1024, 2)
                    }
                    print(f"   ✅ {product_id}: Conectado - Fecha: {meta.get('date', 'N/A')}")
                except json.JSONDecodeError:
                    results[product_id] = {"status": "❌ ERROR JSON", "error": "Respuesta no es JSON válido"}
                    print(f"   ❌ {product_id}: Error al parsear JSON")
            else:
                results[product_id] = {"status": f"❌ HTTP {response.status_code}", "error": response.reason}
                print(f"   ❌ {product_id}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[product_id] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {product_id}: Timeout")
        except requests.exceptions.ConnectionError:
            results[product_id] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {product_id}: Sin conexión")
        except Exception as e:
            results[product_id] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {product_id}: {str(e)}")
        
        # Pausa para no sobrecargar el servidor
        time.sleep(1)
    
    return results

def test_api_rest():
    """
    Prueba acceso a API REST Orphadata
    Basado en: context_orphanet.md sección 4
    """
    print("\n🌐 PRUEBA 2: API REST Orphadata")
    print("-" * 60)
    
    # URLs de la API
    api_urls = [
        "https://api.orphadata.com",
        "https://orphanetapi.developer.azure-api.net"
    ]
    
    results = {}
    
    for api_url in api_urls:
        try:
            print(f"🔗 Probando {api_url}...")
            
            headers = {"User-Agent": USER_AGENT}
            
            # Prueba básica de conectividad
            response = requests.get(api_url, timeout=TIMEOUT, headers=headers)
            
            results[api_url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "size_kb": round(len(response.content) / 1024, 2)
            }
            
            if response.status_code < 400:
                print(f"   ✅ {api_url}: Conectado - HTTP {response.status_code}")
            else:
                print(f"   ❌ {api_url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[api_url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {api_url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[api_url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {api_url}: Sin conexión")
        except Exception as e:
            results[api_url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {api_url}: {str(e)}")
        
        time.sleep(1)
    
    return results

def test_sparql_endpoints():
    """
    Prueba acceso a endpoints SPARQL (ORDO/HOOM)
    Basado en: context_orphanet.md sección 5
    """
    print("\n🔍 PRUEBA 3: Endpoints SPARQL (ORDO/HOOM)")
    print("-" * 60)
    
    # Endpoints SPARQL
    sparql_endpoints = [
        "https://www.orphadata.com/sparql-ordo",
        "https://www.orphadata.com/sparql-hoom"
    ]
    
    results = {}
    
    for endpoint in sparql_endpoints:
        try:
            print(f"🔗 Probando {endpoint}...")
            
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/sparql-results+json"
            }
            
            # Query SPARQL básica para probar conectividad
            query = """
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object
            }
            LIMIT 1
            """
            
            params = {"query": query}
            response = requests.get(endpoint, params=params, headers=headers, timeout=TIMEOUT)
            
            results[endpoint] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "size_kb": round(len(response.content) / 1024, 2)
            }
            
            if response.status_code < 400:
                print(f"   ✅ {endpoint}: Conectado - HTTP {response.status_code}")
            else:
                print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[endpoint] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {endpoint}: Timeout")
        except requests.exceptions.ConnectionError:
            results[endpoint] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {endpoint}: Sin conexión")
        except Exception as e:
            results[endpoint] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {endpoint}: {str(e)}")
        
        time.sleep(1)
    
    return results

def test_ontology_access():
    """
    Prueba acceso directo a ontología ORDO
    Basado en: context_orphanet.md sección 6
    """
    print("\n🧬 PRUEBA 4: Acceso a Ontología ORDO")
    print("-" * 60)
    
    ontology_urls = [
        "http://www.orphadata.com/ontologies/ORDO_4.2.owl",
        "https://www.orphadata.com/ontologies/ORDO_4.2.owl"
    ]
    
    results = {}
    
    for onto_url in ontology_urls:
        try:
            print(f"🔗 Probando {onto_url}...")
            
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/rdf+xml"
            }
            
            # Solo probamos el HEAD para no descargar todo el archivo
            response = requests.head(onto_url, headers=headers, timeout=TIMEOUT)
            
            results[onto_url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "content_length": response.headers.get("content-length", "N/A"),
                "last_modified": response.headers.get("last-modified", "N/A")
            }
            
            if response.status_code < 400:
                size_mb = "N/A"
                if response.headers.get("content-length"):
                    size_mb = round(int(response.headers["content-length"]) / 1024 / 1024, 2)
                print(f"   ✅ {onto_url}: Conectado - Tamaño: {size_mb} MB")
            else:
                print(f"   ❌ {onto_url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[onto_url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {onto_url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[onto_url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {onto_url}: Sin conexión")
        except Exception as e:
            results[onto_url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {onto_url}: {str(e)}")
        
        time.sleep(1)
    
    return results

def generate_report(results):
    """Genera reporte consolidado de conectividad"""
    print("\n📊 REPORTE DE CONECTIVIDAD ORPHANET")
    print("=" * 80)
    
    total_tests = 0
    successful_tests = 0
    
    for category, data in results.items():
        print(f"\n🔸 {category}")
        print("-" * 40)
        
        for service, result in data.items():
            total_tests += 1
            status = result.get("status", "❌ DESCONOCIDO")
            
            if "✅" in status:
                successful_tests += 1
                
            print(f"   {service}")
            print(f"   └─ {status}")
            
            if "fecha" in result:
                print(f"   └─ Última actualización: {result['fecha']}")
            if "error" in result:
                print(f"   └─ Error: {result['error']}")
    
    # Resumen
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 RESUMEN GENERAL")
    print("=" * 80)
    print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 ESTADO: EXCELENTE CONECTIVIDAD")
    elif success_rate >= 60:
        print("⚠️  ESTADO: CONECTIVIDAD PARCIAL")
    else:
        print("❌ ESTADO: PROBLEMAS DE CONECTIVIDAD")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES")
    print("-" * 40)
    
    if successful_tests > 0:
        print("✅ Orphanet está accesible para integración")
        print("✅ Puedes proceder con la homologación de códigos")
        print("✅ Recomendado: Usar free products para descarga masiva")
        
        if "API REST" in str(results):
            print("⚠️  API REST requiere token OAuth2 para acceso completo")
            
    else:
        print("❌ Problemas de conectividad detectados")
        print("❌ Verificar conexión a internet")
        print("❌ Orphanet podría estar en mantenimiento")
    
    print("\n" + "=" * 80)
    
    return success_rate

def save_report(results, filename="orphanet_connectivity_report.json"):
    """Guarda reporte en archivo JSON"""
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "metadata": {
            "python_version": sys.version,
            "script_version": "1.0",
            "timeout": TIMEOUT
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Reporte guardado: {filename}")

def main():
    """Función principal"""
    print_banner()
    
    # Ejecutar todas las pruebas
    all_results = {}
    
    try:
        all_results["Free Products"] = test_free_products()
        all_results["API REST"] = test_api_rest()
        all_results["SPARQL Endpoints"] = test_sparql_endpoints()
        all_results["Ontología ORDO"] = test_ontology_access()
        
        # Generar reporte
        success_rate = generate_report(all_results)
        
        # Guardar reporte
        save_report(all_results)
        
        return success_rate
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
        return 0
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        return 0

if __name__ == "__main__":
    success_rate = main()
    sys.exit(0 if success_rate > 0 else 1)
