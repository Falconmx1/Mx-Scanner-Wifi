"""
Módulo de utilidades para Mx Scanner Wifi
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import platform

class Utils:
    """Clase con funciones de utilidad"""
    
    @staticmethod
    def save_results(networks: List[Dict], analysis: Dict, format: str = 'json', filename: Optional[str] = None):
        """
        Guarda los resultados en un archivo
        
        Args:
            networks: Lista de redes
            analysis: Análisis completo
            format: Formato de salida ('json' o 'csv')
            filename: Nombre del archivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'wifi_scan_{timestamp}.{format}'
        
        if format.lower() == 'json':
            Utils._save_json(networks, analysis, filename)
        elif format.lower() == 'csv':
            Utils._save_csv(networks, filename)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    @staticmethod
    def _save_json(networks: List[Dict], analysis: Dict, filename: str):
        """Guarda en formato JSON"""
        data = {
            'scan_date': datetime.now().isoformat(),
            'total_networks': len(networks),
            'networks': networks,
            'analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Resultados guardados en: {filename}")
    
    @staticmethod
    def _save_csv(networks: List[Dict], filename: str):
        """Guarda en formato CSV"""
        if not networks:
            print("⚠️ No hay redes para guardar")
            return
        
        # Definir campos
        fields = [
            'ssid', 'bssid', 'vendor', 'channel', 'band',
            'frequency', 'security', 'signal_percentage',
            'signal_dbm', 'signal_quality', 'timestamp'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for net in networks:
                signal = net.get('signal', {})
                row = {
                    'ssid': net.get('ssid', 'Unknown'),
                    'bssid': net.get('bssid', 'N/A'),
                    'vendor': net.get('vendor', 'Desconocido'),
                    'channel': net.get('channel', '?'),
                    'band': net.get('band', ''),
                    'frequency': net.get('frequency', 0),
                    'security': net.get('security', 'Unknown'),
                    'signal_percentage': signal.get('percentage', 0),
                    'signal_dbm': signal.get('dbm', 0),
                    'signal_quality': signal.get('quality', 'Mala'),
                    'timestamp': net.get('timestamp', '')
                }
                writer.writerow(row)
        
        print(f"✅ Resultados guardados en: {filename}")
    
    @staticmethod
    def load_results(filename: str) -> Dict:
        """
        Carga resultados guardados
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Dict: Datos cargados
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    return json.load(f)
                else:
                    print("⚠️ Solo se soporta formato JSON")
                    return {}
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {filename}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Error al decodificar JSON: {filename}")
            return {}
    
    @staticmethod
    def get_network_interfaces() -> List[Dict]:
        """
        Obtiene información de todas las interfaces de red
        
        Returns:
            List[Dict]: Lista de interfaces de red
        """
        interfaces = []
        
        try:
            if platform.system() == 'Windows':
                # Windows
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                current_iface = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if 'Adaptador' in line or 'Adapter' in line:
                        if current_iface and current_iface.get('name'):
                            interfaces.append(current_iface)
                        current_iface = {'name': line.replace('Adaptador de', '').strip().strip(':')}
                    
                    elif 'Direcci' in line and ':' in line and 'MAC' not in line:
                        if 'IPv4' in line or 'Dirección IPv4' in line:
                            ip = line.split(':', 1)[1].strip()
                            if ip != '' and ip != 'N/A':
                                current_iface['ip'] = ip
                    
                    elif 'Dirección física' in line or 'Physical Address' in line:
                        mac = line.split(':', 1)[1].strip()
                        if mac != '' and mac != 'N/A':
                            current_iface['mac'] = mac
                
                if current_iface and current_iface.get('name'):
                    interfaces.append(current_iface)
            
            else:
                # Linux/macOS
                result = subprocess.run(
                    ['ifconfig'],
                    capture_output=True,
                    text=True
                )
                
                current_iface = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if line and not line.startswith(' ') and ':' in line:
                        if current_iface and current_iface.get('name'):
                            interfaces.append(current_iface)
                        current_iface = {'name': line.split(':')[0]}
                    
                    elif 'inet ' in line and 'netmask' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'inet' and i+1 < len(parts):
                                current_iface['ip'] = parts[i+1]
                    
                    elif 'ether' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'ether' and i+1 < len(parts):
                                current_iface['mac'] = parts[i+1]
                
                if current_iface and current_iface.get('name'):
                    interfaces.append(current_iface)
        
        except Exception as e:
            print(f"Error obteniendo interfaces: {e}")
        
        return interfaces
    
    @staticmethod
    def check_dependencies() -> Dict:
        """
        Verifica que todas las dependencias estén instaladas
        
        Returns:
            Dict: Estado de las dependencias
        """
        dependencies = {
            'scapy': False,
            'wifi': False,
            'colorama': False,
            'tabulate': False,
            'netifaces': False
        }
        
        for dep in dependencies.keys():
            try:
                __import__(dep)
                dependencies[dep] = True
            except ImportError:
                pass
        
        return dependencies
    
    @staticmethod
    def format_bssid(bssid: str) -> str:
        """
        Formatea un BSSID para asegurar formato correcto
        
        Args:
            bssid: BSSID a formatear
            
        Returns:
            str: BSSID formateado
        """
        # Eliminar espacios y convertir a mayúsculas
        bssid = bssid.strip().upper()
        
        # Asegurar formato XX:XX:XX:XX:XX:XX
        if ':' not in bssid:
            # Si no tiene dos puntos, insertarlos cada 2 caracteres
            parts = [bssid[i:i+2] for i in range(0, len(bssid), 2)]
            return ':'.join(parts)
        
        return bssid
    
    @staticmethod
    def generate_network_summary(networks: List[Dict]) -> str:
        """
        Genera un resumen textual de las redes
        
        Args:
            networks: Lista de redes
            
        Returns:
            str: Resumen en texto plano
        """
        summary = []
        summary.append(f"Total de redes: {len(networks)}")
        
        if networks:
            # Seguridad
            secure = len([n for n in networks if 'WPA' in n.get('security', '')])
            open_networks = len([n for n in networks if n.get('security') == 'Abierta'])
            summary.append(f"Redes seguras: {secure}")
            summary.append(f"Redes abiertas: {open_networks}")
            
            # Banda
            bands = {}
            for n in networks:
                band = n.get('band', 'Desconocida')
                bands[band] = bands.get(band, 0) + 1
            
            for band, count in bands.items():
                summary.append(f"Redes en {band}: {count}")
            
            # Fabricantes principales
            vendors = {}
            for n in networks:
                vendor = n.get('vendor', 'Desconocido')
                vendors[vendor] = vendors.get(vendor, 0) + 1
            
            top_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_vendors:
                summary.append(f"Fabricantes principales: {', '.join([f'{v} ({c})' for v, c in top_vendors])}")
            
            # Señal promedio
            signals = [n.get('signal', {}).get('percentage', 0) for n in networks if n.get('signal')]
            if signals:
                avg_signal = sum(signals) / len(signals)
                summary.append(f"Señal promedio: {avg_signal:.0f}%")
        
        return '\n'.join(summary)
