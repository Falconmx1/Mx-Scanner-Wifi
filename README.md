# Mx Scanner Wifi

**Mx Scanner Wifi** es una herramienta avanzada de escaneo y análisis de redes WiFi desarrollada en Python. Está diseñada para proporcionar información detallada y profesional sobre el entorno inalámbrico cercano, ideal para administradores de redes y entusiastas de la ciberseguridad.

## 📡 Características Principales

*   **Escaneo Detallado de Redes:** Muestra SSID (nombre), BSSID (MAC address del router con identificación del fabricante), canal y frecuencia (2.4/5 GHz).
*   **Medición Precisa de Señal:** Visualización de la intensidad de la señal (RSSI) en dBm, con un porcentaje y una barra gráfica intuitiva.
*   **Análisis de Seguridad:** Detecta automáticamente el protocolo de seguridad: WPA2, WPA3, WEP o redes abiertas.
*   **Análisis de Canales:** Identifica canales congestionados y ofrece recomendaciones para optimizar el rendimiento de tu red.
*   **Recomendaciones Inteligentes:** Sugiere la mejor red disponible basándose en la señal, seguridad y estado de los canales.
*   **Información de Interfaz:** Muestra detalles técnicos como el modo, ESSID, bitrate y potencia de transmisión (Tx-Power).

## 🚀 Instalación

Sigue estos pasos para instalar y ejecutar la herramienta en tu sistema.

```bash
# 1. Clonar el repositorio
git clone https://github.com/Falconmx1/Mx-Scanner-Wifi.git
cd Mx-Scanner-Wifi

# 2. (Opcional) Crear y activar un entorno virtual
# python -m venv venv
# source venv/bin/activate  # En Linux/macOS
# .\venv\Scripts\activate   # En Windows

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Ejecutar la herramienta (ejemplo)
python src/main.py

💻 Uso Básico
Aquí tienes un ejemplo rápido de cómo usar la herramienta en tu propio código:
from src.scanner import WifiScanner
from src.analyzer import NetworkAnalyzer

# Inicializar y escanear
scanner = WifiScanner()
networks = scanner.scan()

# Analizar los resultados
analyzer = NetworkAnalyzer(networks)
analysis = analyzer.analyze_all()

# Mostrar la información (depende de tu implementación en visualizer.py)
# visualizer.display_networks()

📊 Ejemplo de Salida
==========================================
        MX SCANNER WIFI v1.0.0
==========================================

📶 REDES ENCONTRADAS (8)
--------------------------------------------------
SSID: MiCasaWiFi_5G
BSSID: 00:1A:2B:3C:4D:5E (TP-Link)
Canal: 36 (5 GHz) | Frecuencia: 5180 MHz
Señal: ████████░░ 76% (-58 dBm)
Seguridad: WPA3-Personal
Dispositivos: 6 conectados estimados
--------------------------------------------------
SSID: RedVecinos
BSSID: 00:1A:2B:3C:4D:5F (Netgear)
Canal: 6 (2.4 GHz) | Frecuencia: 2437 MHz
Señal: ████░░░░░░ 40% (-70 dBm)
Seguridad: WPA2-PSK (AES)

📊 ANÁLISIS DE CANALES
--------------------------------------------------
Canales congestionados (2.4 GHz): 1, 6, 11
Canales recomendados (2.4 GHz): 3, 8
Canales congestionados (5 GHz): 36, 40
Canales recomendados (5 GHz): 48, 52

🎯 RECOMENDACIONES
--------------------------------------------------
✅ Mejor red por señal: MiCasaWiFi_5G (76%)
✅ Mejor red por seguridad: MiCasaWiFi_5G (WPA3)
⚠️ Canal más congestionado: Canal 6 (4 redes)
💡 Considera cambiar tu router al canal 3 para mejor rendimiento.

🤝 Contribuciones
Las contribuciones son bienvenidas. Para contribuir:

1. Haz un Fork del proyecto.

2. Crea tu rama de características (git checkout -b feature/NuevaCaracteristica).

3. Realiza tus cambios y haz commit (git commit -m 'Agrega nueva característica').

4. Sube tus cambios a la rama (git push origin feature/NuevaCaracteristica).

5. Abre un Pull Request.

📄 Licencia
Distribuido bajo la Licencia MIT. Consulta el archivo LICENSE para más información.

✒️ Autor
Falconmx1 - Perfil de GitHub
