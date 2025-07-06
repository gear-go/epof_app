#!/usr/bin/env python3
"""
Script mejorado para validar conectividad con Orphanet/Orphadata
Versión 2.0 - URLs actualizadas

Basado en documentación oficial y URLs verificadas
Autor: Análisis GRD Enfermedades Raras
Fecha: Julio 2025
"""

import requests
import json
import time
from datetime import datetime
import sys
import warnings
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

# Configuración mejorada
TIMEOUT = 10
USER_AGENT = "OrphanetValidator/2.0 (Research/Colombia)"

def print_banner():
    """Imprime banner de inicio"""
    print("=" * 80)
    print("🔍 VALIDADOR DE CONECTIVIDAD ORPHANET v2.0")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("=" * 80)

def test_orphanet_main():
    """Prueba acceso al sitio principal de Orphanet"""
    print("\n🏠 PRUEBA 1: Sitio Principal Orphanet")
    print("-" * 60)
    
    urls_principales = [
        "https://www.orpha.net",
        "http://www.orpha.net",
        "https://www.orphadata.org",
        "http://www.orphadata.org"
    ]
    
    results = {}
    
    for url in urls_principales:
        try:
            print(f"🔗 Probando {url}...")
            
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, timeout=TIMEOUT, headers=headers, verify=False)
            
            results[url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "size_kb": round(len(response.content) / 1024, 2),
                "server": response.headers.get("server", "N/A")
            }
            
            if response.status_code < 400:
                print(f"   ✅ {url}: Conectado - HTTP {response.status_code}")
            else:
                print(f"   ❌ {url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {url}: Sin conexión")
        except Exception as e:
            results[url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {url}: {str(e)}")
        
        time.sleep(0.5)
    
    return results

def test_orphadata_files():
    """Prueba acceso a archivos de Orphadata"""
    print("\n📁 PRUEBA 2: Archivos de Datos Orphadata")
    print("-" * 60)
    
    # URLs directas conocidas de archivos
    file_urls = [
        "http://www.orphadata.org/cgi-bin/rare_free.html",
        "https://www.orphadata.org/cgi-bin/rare_free.html",
        "http://www.orphadata.org/data/xml/en_product1.xml",
        "http://www.orphadata.org/data/xml/en_product3.xml"
    ]
    
    results = {}
    
    for url in file_urls:
        try:
            print(f"📄 Probando {url}...")
            
            headers = {"User-Agent": USER_AGENT}
            # Solo HEAD request para no descargar archivos grandes
            response = requests.head(url, timeout=TIMEOUT, headers=headers, verify=False)
            
            results[url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "content_length": response.headers.get("content-length", "N/A"),
                "last_modified": response.headers.get("last-modified", "N/A")
            }
            
            if response.status_code < 400:
                size_info = "N/A"
                if response.headers.get("content-length"):
                    size_kb = round(int(response.headers["content-length"]) / 1024, 2)
                    size_info = f"{size_kb} KB"
                print(f"   ✅ {url}: Disponible - Tamaño: {size_info}")
            else:
                print(f"   ❌ {url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {url}: Sin conexión")
        except Exception as e:
            results[url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {url}: {str(e)}")
        
        time.sleep(0.5)
    
    return results

def test_orphanet_api_alternative():
    """Prueba APIs alternativas y recursos conocidos"""
    print("\n🌐 PRUEBA 3: APIs y Recursos Alternativos")
    print("-" * 60)
    
    # URLs alternativas conocidas
    api_urls = [
        "https://api.orphacode.org",
        "http://api.orphacode.org",
        "https://www.orphadata.com/api",
        "http://www.orphadata.com/api"
    ]
    
    results = {}
    
    for url in api_urls:
        try:
            print(f"🔗 Probando {url}...")
            
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, timeout=TIMEOUT, headers=headers, verify=False)
            
            results[url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "size_kb": round(len(response.content) / 1024, 2)
            }
            
            if response.status_code < 400:
                print(f"   ✅ {url}: Conectado - HTTP {response.status_code}")
            else:
                print(f"   ❌ {url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {url}: Sin conexión")
        except Exception as e:
            results[url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {url}: {str(e)}")
        
        time.sleep(0.5)
    
    return results

def test_orphanet_search():
    """Prueba funcionalidad de búsqueda de Orphanet"""
    print("\n🔍 PRUEBA 4: Funcionalidad de Búsqueda Orphanet")
    print("-" * 60)
    
    # URLs de búsqueda conocidas
    search_urls = [
        "https://www.orpha.net/consor/cgi-bin/Disease_Search.php?lng=EN",
        "http://www.orpha.net/consor/cgi-bin/Disease_Search.php?lng=EN"
    ]
    
    results = {}
    
    for url in search_urls:
        try:
            print(f"🔍 Probando {url}...")
            
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, timeout=TIMEOUT, headers=headers, verify=False)
            
            results[url] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "content_type": response.headers.get("content-type", "N/A"),
                "size_kb": round(len(response.content) / 1024, 2),
                "has_search_form": "search" in response.text.lower() or "disease" in response.text.lower()
            }
            
            if response.status_code < 400:
                search_available = "✅ Disponible" if results[url]["has_search_form"] else "⚠️ Sin formulario"
                print(f"   ✅ {url}: Conectado - Búsqueda: {search_available}")
            else:
                print(f"   ❌ {url}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[url] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ {url}: Timeout")
        except requests.exceptions.ConnectionError:
            results[url] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 {url}: Sin conexión")
        except Exception as e:
            results[url] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ {url}: {str(e)}")
        
        time.sleep(0.5)
    
    return results

def test_manual_search():
    """Prueba búsqueda manual de una enfermedad conocida"""
    print("\n🧬 PRUEBA 5: Búsqueda Manual de Enfermedad")
    print("-" * 60)
    
    # Términos de búsqueda de nuestro dataset
    search_terms = ["Marfan", "Alport", "Huntington", "Acondrogénesis", "Acromegalia", "Acalasia primaria"]
    base_url = "https://www.orpha.net/consor/cgi-bin/Disease_Search.php"
    
    results = {}
    
    for term in search_terms:
        try:
            print(f"🔍 Buscando '{term}'...")
            
            params = {
                "lng": "EN",
                "data_id": "Pat",
                "search": "Disease_Search_Simple",
                "Typ": "Pat",
                "diseaseGroup": term
            }
            
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(base_url, params=params, timeout=TIMEOUT, headers=headers, verify=False)
            
            # Buscar indicadores de resultados en la respuesta
            has_results = any(indicator in response.text.lower() for indicator in [
                "orpha number", "orphanet", "disease", "disorder", "syndrome"
            ])
            
            results[f"search_{term}"] = {
                "status": f"✅ HTTP {response.status_code}" if response.status_code < 400 else f"❌ HTTP {response.status_code}",
                "search_term": term,
                "has_results": has_results,
                "content_size_kb": round(len(response.content) / 1024, 2)
            }
            
            if response.status_code < 400:
                result_status = "✅ Con resultados" if has_results else "⚠️ Sin resultados"
                print(f"   ✅ Búsqueda '{term}': {result_status}")
            else:
                print(f"   ❌ Búsqueda '{term}': HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[f"search_{term}"] = {"status": "⏰ TIMEOUT", "error": f"Timeout después de {TIMEOUT}s"}
            print(f"   ⏰ Búsqueda '{term}': Timeout")
        except requests.exceptions.ConnectionError:
            results[f"search_{term}"] = {"status": "🔌 SIN CONEXIÓN", "error": "Error de conexión"}
            print(f"   🔌 Búsqueda '{term}': Sin conexión")
        except Exception as e:
            results[f"search_{term}"] = {"status": "❌ ERROR", "error": str(e)}
            print(f"   ❌ Búsqueda '{term}': {str(e)}")
        
        time.sleep(1)  # Más tiempo entre búsquedas
    
    return results

def generate_enhanced_report(results):
    """Genera reporte mejorado de conectividad"""
    print("\n📊 REPORTE DETALLADO DE CONECTIVIDAD ORPHANET")
    print("=" * 80)
    
    total_tests = 0
    successful_tests = 0
    
    for category, data in results.items():
        print(f"\n🔸 {category}")
        print("-" * 50)
        
        for service, result in data.items():
            total_tests += 1
            status = result.get("status", "❌ DESCONOCIDO")
            
            if "✅" in status:
                successful_tests += 1
                
            print(f"   📋 {service}")
            print(f"   └─ Estado: {status}")
            
            # Información adicional según el tipo de resultado
            if "content_type" in result:
                print(f"   └─ Tipo: {result['content_type']}")
            if "size_kb" in result:
                print(f"   └─ Tamaño: {result['size_kb']} KB")
            if "has_results" in result:
                result_text = "✅ Sí" if result['has_results'] else "❌ No"
                print(f"   └─ Resultados: {result_text}")
            if "error" in result:
                print(f"   └─ Error: {result['error']}")
    
    # Resumen mejorado
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 ANÁLISIS GENERAL")
    print("=" * 80)
    print(f"✅ Conexiones exitosas: {successful_tests}/{total_tests}")
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    
    # Estado general
    if success_rate >= 70:
        print("🎉 ESTADO: ORPHANET ACCESIBLE")
        status_icon = "🟢"
    elif success_rate >= 40:
        print("⚠️  ESTADO: ACCESO PARCIAL A ORPHANET")
        status_icon = "🟡"
    else:
        print("❌ ESTADO: PROBLEMAS GRAVES DE ACCESO")
        status_icon = "🔴"
    
    # Recomendaciones específicas
    print(f"\n💡 RECOMENDACIONES ESPECÍFICAS")
    print("-" * 50)
    
    if successful_tests > 0:
        print("✅ Orphanet está parcialmente accesible")
        print("✅ Se puede proceder con homologación manual de códigos")
        print("✅ Usar búsquedas directas en el sitio web como alternativa")
        
        if success_rate < 70:
            print("⚠️  APIs automáticas pueden estar limitadas")
            print("⚠️  Considerar extracción manual o semi-automática")
        
        print("\n🔧 ESTRATEGIAS SUGERIDAS:")
        print("   1. Búsqueda manual en orpha.net para validación")
        print("   2. Extracción de páginas web específicas")
        print("   3. Uso de códigos Orphá como referencia cruzada")
        print("   4. Integración con APIs cuando estén disponibles")
        
    else:
        print("❌ Orphanet no está accesible actualmente")
        print("❌ Verificar conexión a internet")
        print("❌ Orphanet podría estar en mantenimiento")
        print("⏰ Reintentar en unas horas")
    
    print(f"\n{status_icon} Estado final: {success_rate:.1f}% de conectividad")
    print("=" * 80)
    
    return success_rate, status_icon

def main():
    """Función principal mejorada"""
    print_banner()
    
    # Ejecutar todas las pruebas
    all_results = {}
    
    try:
        all_results["Sitio Principal"] = test_orphanet_main()
        all_results["Archivos de Datos"] = test_orphadata_files()
        all_results["APIs Alternativas"] = test_orphanet_api_alternative()
        all_results["Funcionalidad Búsqueda"] = test_orphanet_search()
        all_results["Búsqueda Manual"] = test_manual_search()
        
        # Generar reporte mejorado
        success_rate, status_icon = generate_enhanced_report(all_results)
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "status_icon": status_icon,
            "test_results": all_results,
            "metadata": {
                "script_version": "2.0",
                "python_version": sys.version,
                "timeout": TIMEOUT,
                "total_tests": sum(len(data) for data in all_results.values())
            }
        }
        
        with open("orphanet_connectivity_report_v2.json", 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte detallado guardado: orphanet_connectivity_report_v2.json")
        
        return success_rate
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Validación interrumpida por el usuario")
        return 0
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        return 0

if __name__ == "__main__":
    success_rate = main()
    print(f"\n🏁 Validación completada con {success_rate:.1f}% de éxito")
    sys.exit(0 if success_rate > 0 else 1)
