# Guía de Instalación - Mx Scanner Wifi

Esta guía te ayudará a instalar y configurar Mx Scanner Wifi en tu sistema.

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo**: Linux, macOS o Windows
- **Python**: Versión 3.7 o superior
- **Memoria RAM**: 256 MB mínimo
- **Espacio en disco**: 50 MB
- **Adaptador WiFi**: Compatible con escaneo de redes

### Requisitos Adicionales por Sistema Operativo

#### 🔹 Linux
- **Distribuciones**: Ubuntu, Debian, Fedora, Arch Linux, etc.
- **Dependencias del sistema**:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-pip python3-dev wireless-tools network-manager
  
  # Fedora
  sudo dnf install python3-pip python3-devel wireless-tools NetworkManager
  
  # Arch Linux
  sudo pacman -S python-pip python wireless_tools networkmanager

  Permisos: Necesario ejecutar con sudo o como root

🔹 macOS
Versión: macOS 10.14 (Mojave) o superior

Herramientas: Xcode Command Line Tools
xcode-select --install

Permisos: Requiere acceso a la localización para escanear WiFi

🔹 Windows
Versión: Windows 10/11

Dependencias: NetSh disponible (incluido por defecto)

Permisos: Ejecutar como administrador

🚀 Instalación
Método 1: Instalación desde GitHub (Recomendado)
Paso 1: Clonar el repositorio
git clone https://github.com/Falconmx1/Mx-Scanner-Wifi.git
cd Mx-Scanner-Wifi

Paso 2: Crear entorno virtual (Opcional pero recomendado)
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

Paso 3: Instalar dependencias
pip install -r requirements.txt

Paso 4: Instalar la herramienta
pip install -e .

Método 2: Instalación desde PyPI (Próximamente)
pip install mx-scanner-wifi

Método 3: Instalación Manual
Opción A: Usando setup.py
python setup.py install
Opción B: Configurar manualmente
1. Copiar la carpeta src a tu proyecto
2. Instalar las dependencias manualmente:

🔧 Verificación de la Instalación
1. Verificar Python
python --version
# Debe mostrar: Python 3.7 o superior

2. Verificar dependencias
python -c "import scapy, wifi, colorama, tabulate, netifaces; print('✅ Todas las dependencias instaladas')"

3. Probar la herramienta
# Ejecutar el ejemplo básico
python examples/example_usage.py

🛠️ Configuración por Sistema Operativo
🔹 Linux
Permisos de Red
Para escanear redes WiFi en Linux, necesitas permisos especiales:

Opción 1: Usar sudo

sudo python examples/example_usage.py
Opción 2: Añadir usuario al grupo (más seguro)
# Encontrar el grupo de red
groups $USER

# Añadir al grupo netdev (Ubuntu/Debian)
sudo usermod -a -G netdev $USER

# En Arch Linux
sudo usermod -a -G network $USER

# Reinciar sesión para aplicar cambios
Configurar NetworkManager

# Permitir escaneo sin sudo
sudo nano /etc/NetworkManager/NetworkManager.conf
# Añadir:
[main]
plugins=keyfile

[ifupdown]
managed=true

# Reiniciar NetworkManager
sudo systemctl restart NetworkManager
🔹 macOS
Configurar Airport
# Crear enlace simbólico para airport
sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport

# Probar
airport -s

Permisos de Localización
1. Ve a Preferencias del Sistema → Seguridad y Privacidad

2. Selecciona "Privacidad" → "Localización"

3. Permite el acceso a tu terminal o aplicación

🔹 Windows
Ejecutar como Administrador
1. Busca "Símbolo del sistema" o "PowerShell"

2. Click derecho → "Ejecutar como administrador"

3. Navega a la carpeta de la herramienta

4. Ejecuta los comandos

Configurar NetSh
# Verificar que NetSh funciona
netsh wlan show networks

# Si no funciona, asegúrate de tener el adaptador WiFi activo

🐛 Solución de Problemas Comunes
❌ Error: "ModuleNotFoundError: No module named 'scapy'"
# Solución:
pip install scapy

# En caso de problemas en Windows:
pip install scapy==2.4.5

❌ Error: "Permission denied" en Linux
# Solución 1: Usar sudo
sudo python script.py

# Solución 2: Añadir usuario al grupo netdev (ver arriba)

❌ Error: "No se encontraron redes WiFi" en Linux
# Verificar interfaz WiFi
iwconfig

# Activar interfaz si está desactivada
sudo ip link set wlan0 up

# Escanear manualmente
sudo iwlist scan

❌ Error en Windows: "netsh no encontrado"
# Asegurarse de que netsh está disponible
where netsh

# Si no está, reparar la instalación de Windows

❌ Error: "wifi" library fails on newer Python versions
# Solución temporal:
pip install wifi==0.3.8

🧪 Pruebas de Instalación
Ejecutar pruebas unitarias
# Instalar pytest
pip install pytest

# Ejecutar pruebas
pytest tests/

Probar funcionalidad básica
# Crear archivo test_quick.py
from src.scanner import WifiScanner

scanner = WifiScanner()
networks = scanner.scan()
print(f"Encontradas: {len(networks)} redes")

for net in networks[:3]:
    print(f"  {net.get('ssid')} - {net.get('signal', {}).get('percentage', 0)}%")

    📦 Actualización
Actualizar desde GitHub
cd Mx-Scanner-Wifi
git pull origin main
pip install -e .  # Reinstalar

Actualizar dependencias
pip install --upgrade -r requirements.txt

🗑️ Desinstalación
# Eliminar paquete
pip uninstall mx-scanner-wifi

# Eliminar archivos del sistema (opcional)
rm -rf Mx-Scanner-Wifi/

📚 Recursos Adicionales
Documentación de Scapy - https://scapy.readthedocs.io/en/latest/

Guía de WiFi en Linux - https://scapy.readthedocs.io/en/latest/

WiFi en Windows con Python - https://learn.microsoft.com/en-us/windows/win32/nativewifi/about-native-wifi
