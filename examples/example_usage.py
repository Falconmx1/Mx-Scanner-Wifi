"""
Ejemplo de uso de Mx Scanner Wifi
Muestra cómo utilizar las diferentes funcionalidades de la herramienta
"""

import sys
import os
import time
from datetime import datetime

# Añadir el directorio padre al path para poder importar src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scanner import WifiScanner
from src.analyzer import NetworkAnalyzer
from src.visualizer import Visualizer
from src.security import SecurityAnalyzer
from src.utils import Utils

def main():
    """Ejemplo principal de uso de la herramienta"""
    
    print("=" * 60)
    print("  MX SCANNER WIFI - EJEMPLO DE USO")
    print("=" * 60)
    print()
    
    # 1. INICIALIZAR EL ESCÁNER
    print("📡 Iniciando escáner...")
    scanner = WifiScanner()
    
    # 2. ESCANEAR REDES
    print("🔍 Escaneando redes WiFi... (esto puede tomar unos segundos)")
    try:
        networks = scanner.scan()
        print(f"✅ Encontradas {len(networks)} redes\n")
    except Exception as e:
        print(f"❌ Error al escanear: {e}")
        return
    
    if not networks:
        print("⚠️ No se encontraron redes WiFi. Asegúrate de:")
        print("  - Tener un adaptador WiFi activo")
        print("  - Tener permisos de administrador/root")
        print("  - Estar en un área con redes WiFi disponibles")
        return
    
    # 3. OBTENER INFORMACIÓN DE INTERFAZ
    print("🔧 Obteniendo información de la interfaz...")
    interface_info = scanner.get_interface_info()
    if interface_info:
        print(f"  Interfaz: {interface_info.get('interface', 'N/A')}")
        print(f"  Modo: {interface_info.get('mode', 'N/A')}")
        print(f"  ESSID: {interface_info.get('essid', 'N/A')}")
    print()
    
    # 4. ANALIZAR REDES
    print("📊 Analizando redes...")
    analyzer = NetworkAnalyzer(networks)
    analysis = analyzer.analyze_all()
    stats = analyzer.get_network_statistics()
    
    # 5. ANALIZAR SEGURIDAD
    print("🔒 Analizando seguridad...")
    security_analyzer = SecurityAnalyzer(networks)
    security_analysis = security_analyzer.analyze_security()
    
    # 6. VISUALIZAR RESULTADOS
    print("🎨 Mostrando resultados...\n")
    visualizer = Visualizer(analysis)
    
    # Mostrar resumen completo
    visualizer.display_summary(networks, interface_info, stats)
    
    # 7. ANALISIS DE SEGURIDAD ADICIONAL
    print("\n" + "=" * 60)
    print("  ANÁLISIS DE SEGURIDAD DETALLADO")
    print("=" * 60)
    
    # Mostrar ranking de seguridad
    ranking = security_analyzer.get_network_security_ranking()
    if ranking:
        print("\n🏆 Ranking de seguridad de redes:")
        print("-" * 60)
        for i, net in enumerate(ranking[:5], 1):
            emoji = "🟢" if net['security_score'] >= 4 else "🟡" if net['security_score'] >= 3 else "🔴"
            print(f"  {i}. {emoji} {net['ssid'][:20]:<20} {net['security'][:15]:<15} "
                  f"Señal: {net['signal']}%")
    
    # Mostrar vulnerabilidades
    vulnerabilities = security_analysis.get('vulnerabilities', [])
    if vulnerabilities:
        print(f"\n⚠️ Vulnerabilidades encontradas ({len(vulnerabilities)}):")
        print("-" * 60)
        for vuln in vulnerabilities[:3]:
            print(f"  🔴 {vuln['network']}: {vuln['description']}")
            print(f"     Severidad: {vuln['severity']}")
    else:
        print("\n✅ No se encontraron vulnerabilidades significativas")
    
    # 8. GUARDAR RESULTADOS
    print("\n" + "=" * 60)
    print("  GUARDANDO RESULTADOS")
    print("=" * 60)
    
    # Guardar en JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f'scan_results_{timestamp}.json'
    Utils.save_results(networks, analysis, 'json', json_file)
    
    # Guardar en CSV
    csv_file = f'scan_results_{timestamp}.csv'
    Utils.save_results(networks, analysis, 'csv', csv_file)
    
    # 9. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("  RESUMEN FINAL")
    print("=" * 60)
    
    summary = Utils.generate_network_summary(networks)
    print(summary)
    
    # 10. RECOMENDACIONES DE SEGURIDAD
    security_score = security_analysis.get('security_score', {})
    print(f"\n🛡️ Puntuación de seguridad del entorno: {security_score.get('score', 0)}/100")
    print(f"   Nivel: {security_score.get('level', 'Desconocido')} {security_score.get('color', '')}")
    
    print("\n" + "=" * 60)
    print("  ¡ESCANEO COMPLETADO CON ÉXITO!")
    print("=" * 60)

def advanced_example():
    """
    Ejemplo avanzado con funcionalidades específicas
    """
    print("\n" + "=" * 60)
    print("  EJEMPLO AVANZADO")
    print("=" * 60)
    
    scanner = WifiScanner()
    networks = scanner.scan()
    
    if not networks:
        return
    
    # Filtrar redes por banda
    networks_2_4 = [n for n in networks if n.get('band') == '2.4 GHz']
    networks_5 = [n for n in networks if n.get('band') == '5 GHz']
    
    print(f"\n📱 Redes 2.4 GHz: {len(networks_2_4)}")
    print(f"🚀 Redes 5 GHz: {len(networks_5)}")
    
    # Encontrar mejores redes por banda
    if networks_2_4:
        best_2_4 = max(networks_2_4, key=lambda x: x.get('signal', {}).get('percentage', 0))
        print(f"\n📶 Mejor red 2.4 GHz: {best_2_4.get('ssid', 'N/A')} "
              f"({best_2_4.get('signal', {}).get('percentage', 0)}%)")
    
    if networks_5:
        best_5 = max(networks_5, key=lambda x: x.get('signal', {}).get('percentage', 0))
        print(f"📶 Mejor red 5 GHz: {best_5.get('ssid', 'N/A')} "
              f"({best_5.get('signal', {}).get('percentage', 0)}%)")
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias:")
    deps = Utils.check_dependencies()
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"  {status} {dep}")

def interactive_example():
    """
    Ejemplo interactivo con menú de opciones
    """
    print("\n" + "=" * 60)
    print("  MODO INTERACTIVO")
    print("=" * 60)
    
    scanner = WifiScanner()
    networks = scanner.scan()
    
    if not networks:
        return
    
    while True:
        print("\n📋 MENÚ DE OPCIONES:")
        print("  1. Mostrar todas las redes")
        print("  2. Mostrar redes por banda")
        print("  3. Mostrar análisis de canales")
        print("  4. Mostrar recomendaciones")
        print("  5. Mostrar estadísticas de seguridad")
        print("  6. Guardar resultados")
        print("  7. Salir")
        
        choice = input("\n👉 Selecciona una opción (1-7): ").strip()
        
        if choice == '1':
            analyzer = NetworkAnalyzer(networks)
            analysis = analyzer.analyze_all()
            visualizer = Visualizer(analysis)
            visualizer.display_networks(networks)
        
        elif choice == '2':
            # Filtrar por banda
            band = input("Selecciona banda (2.4/5): ").strip()
            filtered = [n for n in networks if band in n.get('band', '')]
            if filtered:
                analyzer = NetworkAnalyzer(filtered)
                analysis = analyzer.analyze_all()
                visualizer = Visualizer(analysis)
                visualizer.display_networks(filtered)
            else:
                print(f"⚠️ No se encontraron redes en {band}")
        
        elif choice == '3':
            analyzer = NetworkAnalyzer(networks)
            analysis = analyzer.analyze_all()
            visualizer = Visualizer(analysis)
            visualizer.display_channel_analysis()
        
        elif choice == '4':
            analyzer = NetworkAnalyzer(networks)
            analysis = analyzer.analyze_all()
            visualizer = Visualizer(analysis)
            visualizer.display_recommendations()
        
        elif choice == '5':
            security_analyzer = SecurityAnalyzer(networks)
            security_analysis = security_analyzer.analyze_security()
            print(f"\n📊 Estadísticas de seguridad:")
            print(f"  Redes seguras: {security_analysis['summary']['secure_networks']}")
            print(f"  Redes inseguras: {security_analysis['summary']['insecure_networks']}")
            print(f"  Tipos de encriptación: {security_analysis['summary']['encryption_types']}")
        
        elif choice == '6':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = input("Nombre del archivo (sin extensión): ").strip()
            if not filename:
                filename = f'scan_{timestamp}'
            
            Utils.save_results(networks, {}, 'json', f'{filename}.json')
            Utils.save_results(networks, {}, 'csv', f'{filename}.csv')
        
        elif choice == '7':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    try:
        # Ejecutar ejemplo principal
        main()
        
        # Ejecutar ejemplo avanzado
        advanced_example()
        
        # Preguntar si quiere modo interactivo
        print("\n" + "=" * 60)
        response = input("¿Quieres probar el modo interactivo? (s/n): ").strip().lower()
        if response == 's':
            interactive_example()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Escaneo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
