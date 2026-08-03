"""
Módulo de escaneo de redes WiFi
"""

import subprocess
import re
import sys
import platform
from typing import List, Dict, Optional
from datetime import datetime
import socket
import struct

class WifiScanner:
    """Clase principal para escanear redes WiFi"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.networks = []
        
    def scan(self) -> List[Dict]:
        """
        Escanea redes WiFi disponibles
        
        Returns:
            List[Dict]: Lista de redes con sus detalles
        """
        if self.os_type == "Linux":
            return self._scan_linux()
        elif self.os_type == "Darwin":  # macOS
            return self._scan_mac()
        elif self.os_type == "Windows":
            return self._scan_windows()
        else:
            raise OSError(f"Sistema operativo no soportado: {self.os_type}")
    
    def _scan_linux(self) -> List[Dict]:
        """Escaneo en Linux usando nmcli o iwlist"""
        try:
            # Intentar con nmcli primero
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,SECURITY,CHAN,SIGNAL', 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return self._parse_nmcli(result.stdout)
            
            # Fallback a iwlist
            result = subprocess.run(
                ['sudo', 'iwlist', 'scan'],
                capture_output=True,
                text=True,
                timeout=15
            )
            return self._parse_iwlist(result.stdout)
            
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout en escaneo. Intentando nuevamente...")
            return []
        except Exception as e:
            print(f"❌ Error en escaneo Linux: {e}")
            return []
    
    def _scan_mac(self) -> List[Dict]:
        """Escaneo en macOS usando airport"""
        try:
            # Encontrar interfaz WiFi
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self._parse_airport(result.stdout)
        except Exception as e:
            print(f"❌ Error en escaneo macOS: {e}")
            return []
    
    def _scan_windows(self) -> List[Dict]:
        """Escaneo en Windows usando netsh"""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            return self._parse_netsh(result.stdout)
        except Exception as e:
            print(f"❌ Error en escaneo Windows: {e}")
            return []
    
    def _parse_nmcli(self, output: str) -> List[Dict]:
        """Parsea la salida de nmcli"""
        networks = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            parts = line.split(':')
            if len(parts) >= 5:
                network = {
                    'ssid': parts[0] if parts[0] != '--' else 'Red Oculta',
                    'bssid': parts[1].upper(),
                    'security': parts[2] if parts[2] != '' else 'Abierta',
                    'channel': parts[3] if parts[3] != '' else '0',
                    'signal': self._parse_signal(parts[4]),
                    'frequency': self._get_frequency(parts[3]),
                    'band': self._get_band(parts[3]),
                    'vendor': self._get_vendor(parts[1]) if len(parts[1]) >= 6 else 'Desconocido',
                    'timestamp': datetime.now().isoformat()
                }
                networks.append(network)
        
        return networks
    
    def _parse_iwlist(self, output: str) -> List[Dict]:
        """Parsea la salida de iwlist"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {}
                # Extraer BSSID
                bssid_match = re.search(r'Address: ([0-9A-F:]+)', line)
                if bssid_match:
                    current_network['bssid'] = bssid_match.group(1)
                    current_network['vendor'] = self._get_vendor(bssid_match.group(1))
            
            elif 'ESSID:' in line:
                ssid = re.search(r'ESSID:"(.+?)"', line)
                current_network['ssid'] = ssid.group(1) if ssid else 'Red Oculta'
            
            elif 'Frequency:' in line:
                freq_match = re.search(r'Frequency:([0-9.]+) GHz', line)
                if freq_match:
                    freq = float(freq_match.group(1))
                    current_network['frequency'] = freq * 1000  # Convertir a MHz
                    current_network['band'] = '5 GHz' if freq > 2.4 else '2.4 GHz'
                    current_network['channel'] = self._get_channel_from_frequency(freq * 1000)
            
            elif 'Signal level=' in line:
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                if signal_match:
                    dbm = int(signal_match.group(1))
                    current_network['signal'] = self._parse_signal(str(dbm))
                    current_network['dbm'] = dbm
            
            elif 'Encryption key:' in line:
                if 'on' in line.lower():
                    current_network['security'] = 'Encriptada'
                else:
                    current_network['security'] = 'Abierta'
            
            elif 'IE:' in line and 'WPA' in line:
                if 'WPA2' in line or 'RSN' in line:
                    current_network['security'] = 'WPA2'
                elif 'WPA' in line:
                    current_network['security'] = 'WPA'
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _parse_airport(self, output: str) -> List[Dict]:
        """Parsea la salida de airport en macOS"""
        networks = []
        lines = output.strip().split('\n')
        
        # Saltar cabecera
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                network = {
                    'ssid': ' '.join(parts[:-5]),
                    'bssid': parts[-5] if len(parts) >= 5 else '00:00:00:00:00:00',
                    'security': self._detect_security_mac(line),
                    'signal': self._parse_signal(parts[-2] if len(parts) >= 2 else '0'),
                    'channel': parts[-1] if len(parts) >= 1 else '0',
                    'frequency': self._get_frequency(parts[-1] if len(parts) >= 1 else '0'),
                    'band': self._get_band(parts[-1] if len(parts) >= 1 else '0'),
                    'vendor': self._get_vendor(parts[-5]) if len(parts) >= 5 else 'Desconocido',
                    'timestamp': datetime.now().isoformat()
                }
                networks.append(network)
        
        return networks
    
    def _parse_netsh(self, output: str) -> List[Dict]:
        """Parsea la salida de netsh en Windows"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'SSID' in line and ':' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {}
                ssid = line.split(':', 1)[1].strip()
                current_network['ssid'] = ssid if ssid else 'Red Oculta'
            
            elif 'BSSID' in line and ':' in line:
                bssid = line.split(':', 1)[1].strip()
                current_network['bssid'] = bssid
                current_network['vendor'] = self._get_vendor(bssid)
            
            elif 'Signal' in line and ':' in line:
                signal = line.split(':', 1)[1].strip().replace('%', '')
                current_network['signal'] = self._parse_signal(signal)
            
            elif 'Radio type' in line and ':' in line:
                radio = line.split(':', 1)[1].strip()
                if '802.11n' in radio or '802.11g' in radio or '802.11b' in radio:
                    current_network['band'] = '2.4 GHz'
                elif '802.11ac' in radio or '802.11a' in radio:
                    current_network['band'] = '5 GHz'
                else:
                    current_network['band'] = radio
            
            elif 'Channel' in line and ':' in line:
                channel = line.split(':', 1)[1].strip()
                current_network['channel'] = channel
                current_network['frequency'] = self._get_frequency(channel)
            
            elif 'Authentication' in line and ':' in line:
                auth = line.split(':', 1)[1].strip()
                if 'WPA2' in auth or 'WPA3' in auth:
                    current_network['security'] = auth
                elif 'WEP' in auth:
                    current_network['security'] = 'WEP'
                elif 'Open' in auth:
                    current_network['security'] = 'Abierta'
                else:
                    current_network['security'] = auth
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _parse_signal(self, signal_str: str) -> Dict:
        """
        Parsea el valor de señal y lo convierte a porcentaje y dBm
        
        Args:
            signal_str: String con el valor de señal
            
        Returns:
            Dict: {'percentage': int, 'dbm': int}
        """
        try:
            signal = int(signal_str.replace('%', '').strip())
            
            # Si es porcentaje, convertir a dBm aproximado
            if signal <= 100 and signal >= 0:
                dbm = int((signal - 100) * -1)
                return {
                    'percentage': signal,
                    'dbm': dbm,
                    'quality': self._get_signal_quality(signal)
                }
            else:
                # Asumir que es dBm (valores negativos)
                dbm = signal
                percentage = max(0, min(100, int(100 + (signal / 100) * 100)))
                return {
                    'percentage': percentage,
                    'dbm': dbm,
                    'quality': self._get_signal_quality(percentage)
                }
        except ValueError:
            return {'percentage': 0, 'dbm': -100, 'quality': 'Mala'}
    
    def _get_signal_quality(self, percentage: int) -> str:
        """Determina la calidad de la señal"""
        if percentage >= 70:
            return 'Excelente'
        elif percentage >= 50:
            return 'Buena'
        elif percentage >= 30:
            return 'Regular'
        else:
            return 'Mala'
    
    def _get_frequency(self, channel: str) -> int:
        """
        Obtiene la frecuencia en MHz a partir del canal
        
        Args:
            channel: Número de canal como string
            
        Returns:
            int: Frecuencia en MHz
        """
        try:
            ch = int(channel)
            
            # Canales 2.4 GHz
            if 1 <= ch <= 14:
                if ch == 14:
                    return 2484
                else:
                    return 2407 + (ch * 5)
            
            # Canales 5 GHz
            elif 36 <= ch <= 165:
                return 5000 + (ch - 36) * 5
            
        except ValueError:
            pass
        
        return 0
    
    def _get_channel_from_frequency(self, frequency_mhz: int) -> str:
        """Obtiene el canal a partir de la frecuencia"""
        freq_map = {
            2412: '1', 2417: '2', 2422: '3', 2427: '4', 2432: '5',
            2437: '6', 2442: '7', 2447: '8', 2452: '9', 2457: '10',
            2462: '11', 2467: '12', 2472: '13', 2484: '14',
            5180: '36', 5200: '40', 5220: '44', 5240: '48',
            5260: '52', 5280: '56', 5300: '60', 5320: '64',
            5500: '100', 5520: '104', 5540: '108', 5560: '112',
            5580: '116', 5600: '120', 5620: '124', 5640: '128',
            5660: '132', 5680: '136', 5700: '140', 5745: '149',
            5765: '153', 5785: '157', 5805: '161', 5825: '165'
        }
        return freq_map.get(frequency_mhz, '0')
    
    def _get_band(self, channel: str) -> str:
        """Determina la banda (2.4/5 GHz) según el canal"""
        try:
            ch = int(channel)
            if 1 <= ch <= 14:
                return '2.4 GHz'
            elif 36 <= ch <= 165:
                return '5 GHz'
        except ValueError:
            pass
        return 'Desconocida'
    
    def _detect_security_mac(self, line: str) -> str:
        """Detecta el tipo de seguridad en macOS"""
        if 'WPA2' in line or 'RSN' in line:
            return 'WPA2-Personal'
        elif 'WPA' in line:
            return 'WPA-Personal'
        elif 'WEP' in line:
            return 'WEP'
        else:
            return 'Abierta'
    
    def _get_vendor(self, mac: str) -> str:
        """
        Identifica el fabricante a partir de la MAC address
        Usa una base de datos local de OUI
        """
        # OUI Database (ejemplos comunes)
        oui_db = {
            '00:1A:2B': 'TP-Link',
            '00:1C:10': 'Netgear',
            '00:1D:AA': 'D-Link',
            '00:1E:2A': 'Cisco',
            '00:14:6C': 'Cisco',
            '00:0C:41': 'Intel',
            '00:16:CB': 'Microsoft',
            '00:18:F8': 'Apple',
            '00:1F:5B': 'Samsung',
            '00:23:4E': 'Linksys',
            '00:1E:13': 'Asus',
            '00:21:6A': 'Dell',
            '00:1D:4F': 'Motorola',
            '00:1E:8C': 'Huawei',
            '00:25:9E': 'Xiaomi',
            '00:23:AA': 'Belkin',
            '00:1C:DF': 'Zyxel',
            '00:26:5A': 'Atheros',
            '00:1B:21': 'Broadcom',
            '00:22:AA': 'Realtek'
        }
        
        # Buscar OUI en la base de datos
        mac_upper = mac.upper()
        for oui, vendor in oui_db.items():
            if mac_upper.startswith(oui):
                return vendor
        
        return 'Desconocido'
    
    def get_interface_info(self) -> Dict:
        """Obtiene información de la interfaz WiFi"""
        try:
            if self.os_type == "Linux":
                return self._get_interface_linux()
            elif self.os_type == "Windows":
                return self._get_interface_windows()
            elif self.os_type == "Darwin":
                return self._get_interface_mac()
        except Exception as e:
            print(f"Error obteniendo info de interfaz: {e}")
            return {}
    
    def _get_interface_linux(self) -> Dict:
        """Obtiene info de interfaz en Linux"""
        info = {}
        try:
            # Nombre de interfaz
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    info['interface'] = line.split()[0]
                    break
            
            # Modo y ESSID
            if info.get('interface'):
                result = subprocess.run(['iwconfig', info['interface']], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Mode:' in line:
                        info['mode'] = line.split('Mode:')[1].split()[0]
                    if 'ESSID:' in line:
                        info['essid'] = line.split('ESSID:')[1].strip('"')
                    if 'Bit Rate' in line:
                        rate = line.split('Bit Rate:')[1].split()[0]
                        info['bitrate'] = f"{rate} Mb/s"
                    if 'Tx-Power' in line:
                        power = line.split('Tx-Power=')[1].split()[0]
                        info['tx_power'] = f"{power} dBm"
            
        except Exception as e:
            print(f"Error obteniendo interfaz Linux: {e}")
        
        return info
    
    def _get_interface_windows(self) -> Dict:
        """Obtiene info de interfaz en Windows"""
        info = {}
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'Name' in line and ':' in line:
                    info['interface'] = line.split(':', 1)[1].strip()
                elif 'Mode' in line and ':' in line:
                    info['mode'] = line.split(':', 1)[1].strip()
                elif 'SSID' in line and ':' in line:
                    info['essid'] = line.split(':', 1)[1].strip()
                elif 'Radio type' in line and ':' in line:
                    info['radio_type'] = line.split(':', 1)[1].strip()
                elif 'Signal' in line and ':' in line:
                    info['signal'] = line.split(':', 1)[1].strip()
                    
        except Exception as e:
            print(f"Error obteniendo interfaz Windows: {e}")
        
        return info
    
    def _get_interface_mac(self) -> Dict:
        """Obtiene info de interfaz en macOS"""
        info = {}
        try:
            result = subprocess.run(['ifconfig', 'en0'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'media:' in line and '802.11' in line:
                    info['interface'] = 'en0'
                    info['media'] = line.strip()
                    break
            
            result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'BSSID' in line:
                    info['bssid'] = line.split(':', 1)[1].strip()
                elif 'SSID' in line:
                    info['ssid'] = line.split(':', 1)[1].strip()
                elif 'MODE' in line:
                    info['mode'] = line.split(':', 1)[1].strip()
                elif 'PHY MODE' in line:
                    info['phy_mode'] = line.split(':', 1)[1].strip()
                elif 'CHANNEL' in line:
                    info['channel'] = line.split(':', 1)[1].strip()
                    
        except Exception as e:
            print(f"Error obteniendo interfaz macOS: {e}")
        
        return info
