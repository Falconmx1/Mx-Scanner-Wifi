```markdown
# Guía de Uso - Mx Scanner Wifi

Esta guía te mostrará cómo utilizar todas las funcionalidades de Mx Scanner Wifi.

## 🚀 Uso Básico

### Ejecutar el Escáner

#### Opción 1: Usar el script principal
```bash
# Linux/macOS
python3 examples/example_usage.py

# Windows
python examples/example_usage.py
Opción 2: Usar la línea de comandos (si instalaste el paquete)
mx-scanner
Opción 3: Importar en tu código Python
from src.scanner import WifiScanner
from src.analyzer import NetworkAnalyzer

# Escanear
scanner = WifiScanner()
networks = scanner.scan()

# Analizar
analyzer = NetworkAnalyzer(networks)
analysis = analyzer.analyze_all()

Salida Típica
============================================================
        MX SCANNER WIFI v1.0.0
============================================================
🔍 Escaneo de redes WiFi completado
📊 4 redes encontradas
============================================================

+---+------------------+------------------+---------+------------------+-------------------+------------------+
| # | SSID             | BSSID            | Canal   | Señal            | Seguridad         | Fabricante       |
+---+------------------+------------------+---------+------------------+-------------------+------------------+
| 1 | RedSegura        | 00:1A:2B:3C:4D:5E | 6       | ██████████ 85%   | WPA3-Personal     | TP-Link          |
| 2 | RedAbierta       | 00:1C:10:11:22:33 | 1       | ██████░░░░ 60%   | Abierta           | Netgear          |
| 3 | RedWPA2          | 00:14:6C:44:55:66 | 36      | ████░░░░░░ 40%   | WPA2-Personal     | Cisco            |
| 4 | RedWEP           | 00:1D:AA:77:88:99 | 11      | ██░░░░░░░░ 25%   | WEP               | D-Link           |
+---+------------------+------------------+---------+------------------+-------------------+------------------+

🎯 RECOMENDACIONES
------------------------------------------------------------
📡 Canal recomendado para 2.4 GHz: 1
🔓 Hay redes abiertas detectadas - evita conectarte a ellas
🛡️ WPA3 disponible - opción más segura
⭐ Mejor red general: RedSegura (Señal: 85%, Seguridad: WPA3-Personal)

📖 Funcionalidades Detalladas
1. Escaneo de Redes
Escaneo Simple
from src.scanner import WifiScanner

scanner = WifiScanner()
networks = scanner.scan()

for network in networks:
    print(f"SSID: {network.get('ssid')}")
    print(f"  BSSID: {network.get('bssid')}")
    print(f"  Señal: {network.get('signal', {}).get('percentage')}%")
    print(f"  Seguridad: {network.get('security')}")
    print()

Escaneo con Detalles
from src.scanner import WifiScanner
from src.analyzer import NetworkAnalyzer
from src.visualizer import Visualizer

scanner = WifiScanner()
networks = scanner.scan()

# Obtener información de interfaz
interface = scanner.get_interface_info()
print(f"Interfaz: {interface.get('interface')}")

# Analizar
analyzer = NetworkAnalyzer(networks)
analysis = analyzer.analyze_all()
stats = analyzer.get_network_statistics()

# Visualizar
visualizer = Visualizer(analysis)
visualizer.display_summary(networks, interface, stats)

2. Análisis de Seguridad
Análisis Básico
from src.security import SecurityAnalyzer

security_analyzer = SecurityAnalyzer(networks)
security_analysis = security_analyzer.analyze_security()

print(f"Redes seguras: {security_analysis['summary']['secure_networks']}")
print(f"Redes inseguras: {security_analysis['summary']['insecure_networks']}")
print(f"Tipos de encriptación: {security_analysis['summary']['encryption_types']}")

Ranking de Seguridad
ranking = security_analyzer.get_network_security_ranking()

for i, net in enumerate(ranking[:5], 1):
    emoji = "🟢" if net['security_score'] >= 4 else "🟡" if net['security_score'] >= 3 else "🔴"
    print(f"{i}. {emoji} {net['ssid']} - {net['security']} ({net['signal']}%)")

Verificar Fortaleza de Contraseña
password_analysis = security_analyzer.check_password_strength("MiContraseñaSegura123!")
print(f"Nivel: {password_analysis['level']}")
print(f"Puntaje: {password_analysis['score']}/{password_analysis['max_score']}")
for feedback in password_analysis['feedback']:
    print(f"  {feedback}")

3. Análisis de Canales
from src.analyzer import NetworkAnalyzer

analyzer = NetworkAnalyzer(networks)
channel_analysis = analyzer._analyze_channel_congestion()

# Ver canales congestionados
for channel, data in channel_analysis['congested_channels'].items():
    print(f"Canal {channel}: {data['network_count']} redes - {data['congestion_level']}")

# Ver canales recomendados
for band, channels in channel_analysis['recommended_channels'].items():
    print(f"Canales recomendados para {band}: {', '.join(map(str, channels))}")

4. Visualización de Datos
Mostrar Todas las Redes
from src.visualizer import Visualizer

visualizer = Visualizer(analysis)
visualizer.display_networks(networks)

Mostrar Resumen Completo
visualizer.display_summary(networks, interface_info, stats)

Mostrar Recomendaciones
visualizer.display_recommendations()

5. Guardar Resultados
Guardar en JSON
from src.utils import Utils

Utils.save_results(networks, analysis, 'json', 'resultados.json')
# Guarda toda la información en formato JSON

Guardar en CSV
Utils.save_results(networks, analysis, 'csv', 'resultados.csv')
# Guarda las redes en formato CSV (más compatible)

Cargar Resultados Guardados
data = Utils.load_results('resultados.json')
networks = data.get('networks', [])
analysis = data.get('analysis', {})

6. Funcionalidades Avanzadas
Filtrar por Banda

# Redes 2.4 GHz
networks_2_4 = [n for n in networks if n.get('band') == '2.4 GHz']

# Redes 5 GHz
networks_5 = [n for n in networks if n.get('band') == '5 GHz']

Encontrar Mejor Red por Señal
best_signal = max(networks, key=lambda x: x.get('signal', {}).get('percentage', 0))
print(f"Mejor red: {best_signal['ssid']} - {best_signal['signal']['percentage']}%")

Encontrar Mejor Red por Seguridad
# Prioridad: WPA3 > WPA2 > WPA > WEP > Abierta
security_priority = {
    'WPA3': 5,
    'WPA2': 4,
    'WPA': 3,
    'WEP': 2,
    'Abierta': 1
}

best_security = max(networks, key=lambda x: security_priority.get(x.get('security'), 0))
print(f"Más segura: {best_security['ssid']} - {best_security['security']}")

Generar Resumen de Redes
summary = Utils.generate_network_summary(networks)
print(summary)
# Muestra: total, seguras, abiertas, distribución de bandas, top fabricantes

7. Modo Interactivo
# Ejecutar el ejemplo interactivo
python -c "from examples.example_usage import interactive_example; interactive_example()"

Menú interactivo:

📋 MENÚ DE OPCIONES:
  1. Mostrar todas las redes
  2. Mostrar redes por banda
  3. Mostrar análisis de canales
  4. Mostrar recomendaciones
  5. Mostrar estadísticas de seguridad
  6. Guardar resultados
  7. Salir

🎯 Casos de Uso Comunes
Caso 1: Auditoría de Seguridad en Casa

from src.scanner import WifiScanner
from src.security import SecurityAnalyzer

scanner = WifiScanner()
networks = scanner.scan()

security_analyzer = SecurityAnalyzer(networks)
security_analysis = security_analyzer.analyze_security()

# Verificar vulnerabilidades
vulnerabilities = security_analysis.get('vulnerabilities', [])
if vulnerabilities:
    print("⚠️ Vulnerabilidades encontradas:")
    for vuln in vulnerabilities:
        print(f"  - {vuln['network']}: {vuln['description']}")
else:
    print("✅ Sin vulnerabilidades significativas")

# Ver puntuación de seguridad
score = security_analysis['security_score']
print(f"\nPuntuación de seguridad: {score['score']}/100 - {score['level']}")

Caso 2: Optimización de WiFi
from src.scanner import WifiScanner
from src.analyzer import NetworkAnalyzer

scanner = WifiScanner()
networks = scanner.scan()

analyzer = NetworkAnalyzer(networks)
channel_analysis = analyzer._analyze_channel_congestion()

# Obtener canal menos congestionado
for band in ['2.4 GHz', '5 GHz']:
    rec_channels = channel_analysis['recommended_channels'].get(band, [])
    if rec_channels:
        print(f"Cambia tu router al canal {rec_channels[0]} para {band}")

Caso 3: Análisis de Competencia (vecinos)
from src.scanner import WifiScanner
from src.utils import Utils

scanner = WifiScanner()
networks = scanner.scan()

# Estadísticas de fabricantes
vendors = {}
for net in networks:
    vendor = net.get('vendor', 'Desconocido')
    vendors[vendor] = vendors.get(vendor, 0) + 1

print("📊 Distribución de fabricantes:")
for vendor, count in sorted(vendors.items(), key=lambda x: x[1], reverse=True):
    print(f"  {vendor}: {count} redes")

Caso 4: Monitoreo Continuo
import time
from src.scanner import WifiScanner

scanner = WifiScanner()

while True:
    networks = scanner.scan()
    print(f"\n[{time.strftime('%H:%M:%S')}] Redes encontradas: {len(networks)}")
    
    # Mostrar cambio en redes
    for net in networks:
        print(f"  {net.get('ssid')} - {net.get('signal', {}).get('percentage')}%")
    
    time.sleep(30)  # Escanear cada 30 segundos

🎨 Personalización
Configurar Colores
from colorama import Fore, Back, Style

# Personalizar colores de salida
print(f"{Fore.CYAN}Mi red WiFi {Fore.GREEN}conectada{Style.RESET_ALL}")

Filtrar Resultados
# Solo redes con WPA2 o WPA3
secure_networks = [
    n for n in networks 
    if 'WPA2' in n.get('security', '') or 'WPA3' in n.get('security', '')
]

# Solo redes con señal > 50%
good_signal = [
    n for n in networks 
    if n.get('signal', {}).get('percentage', 0) > 50
]

Exportar a HTML
import json

def export_html(networks, filename='wifi_report.html'):
    html = f"""
    <html>
    <head><title>Informe WiFi</title></head>
    <body>
    <h1>Redes WiFi Encontradas</h1>
    <table border="1">
    <tr><th>SSID</th><th>Señal</th><th>Seguridad</th></tr>
    """
    
    for net in networks:
        html += f"""
        <tr>
            <td>{net.get('ssid')}</td>
            <td>{net.get('signal', {}).get('percentage', 0)}%</td>
            <td>{net.get('security')}</td>
        </tr>
        """
    
    html += "</table></body></html>"
    
    with open(filename, 'w') as f:
        f.write(html)
    
    print(f"✅ Reporte HTML guardado en {filename}")

export_html(networks)

🚨 Solución de Problemas
Error: No se encuentran redes

# Verificar que el adaptador WiFi está activo
import subprocess
result = subprocess.run(['iwconfig'], capture_output=True, text=True)
print(result.stdout)

# En Linux, verificar permisos
# sudo python script.py

Error: Permiso denegado
# Linux: Ejecutar con sudo
# sudo python script.py

# Windows: Ejecutar como administrador
# Right-click → Run as administrator

# Linux: Ejecutar con sudo
# sudo python script.py

# Windows: Ejecutar como administrador
# Right-click → Run as administrator

# Limitar número de redes mostradas
for net in networks[:10]:
    print(net['ssid'])

# Usar análisis selectivo
analyzer = NetworkAnalyzer(networks[:20])  # Solo primeras 20 redes

📚 Ejemplos Adicionales
Script para Cambiar Automáticamente al Mejor Canal

def get_best_channel():
    scanner = WifiScanner()
    networks = scanner.scan()
    analyzer = NetworkAnalyzer(networks)
    channel_analysis = analyzer._analyze_channel_congestion()
    
    # Mejor canal 2.4 GHz
    rec = channel_analysis['recommended_channels']['2.4 GHz']
    return rec[0] if rec else 6

print(f"Cambia tu router al canal: {get_best_channel()}")

Script de Alertas de Redes Inseguras
def check_insecure_networks():
    scanner = WifiScanner()
    networks = scanner.scan()
    
    insecure = [n for n in networks if n.get('security') in ['Abierta', 'WEP']]
    
    if insecure:
        print("⚠️ ¡Redes inseguras detectadas!")
        for net in insecure:
            print(f"  - {net['ssid']} ({net['security']})")
        return True
    else:
        print("✅ Todas las redes son seguras")
        return False

check_insecure_networks()
