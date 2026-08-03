"""
Módulo de visualización de datos WiFi
"""

from typing import List, Dict
import colorama
from colorama import Fore, Back, Style
from tabulate import tabulate
import os
import platform

# Inicializar colorama
colorama.init(autoreset=True)

class Visualizer:
    """Clase para visualizar información de redes WiFi"""
    
    def __init__(self, analysis: Dict):
        self.analysis = analysis
        self.terminal_width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Obtiene el ancho de la terminal"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80
    
    def display_header(self):
        """Muestra el encabezado de la herramienta"""
        print("\n" + "=" * self.terminal_width)
        print(f"{Fore.CYAN}{Style.BRIGHT}{'MX SCANNER WIFI v1.0.0':^{self.terminal_width}}")
        print("=" * self.terminal_width)
        print(f"{Fore.YELLOW}🔍 Escaneo de redes WiFi completado")
        print(f"📊 {len(self.analysis.get('networks', []))} redes encontradas")
        print("=" * self.terminal_width + "\n")
    
    def display_networks(self, networks: List[Dict]):
        """
        Muestra las redes en formato tabular con indicadores visuales
        
        Args:
            networks: Lista de redes a mostrar
        """
        if not networks:
            print(f"{Fore.RED}❌ No se encontraron redes WiFi")
            return
        
        # Preparar datos para la tabla
        table_data = []
        for i, net in enumerate(networks, 1):
            signal = net.get('signal', {})
            
            # Crear barra de señal
            signal_bar = self._create_signal_bar(signal.get('percentage', 0))
            
            # Color según seguridad
            security_color = self._get_security_color(net.get('security', ''))
            
            # Emoji según banda
            band_emoji = "📱" if "2.4" in net.get('band', '') else "🚀"
            
            table_data.append([
                f"{Fore.WHITE}{i}",
                f"{Fore.GREEN}{net.get('ssid', 'Unknown')[:25]}",
                f"{Fore.YELLOW}{net.get('bssid', 'N/A')}",
                f"{band_emoji} {net.get('channel', '?')}",
                f"{signal_bar} {signal.get('percentage', 0)}%",
                f"{security_color}{net.get('security', 'Unknown')}",
                f"{Fore.CYAN}{net.get('vendor', 'Desconocido')[:12]}"
            ])
        
        # Mostrar tabla
        headers = [
            "#", "SSID", "BSSID", "Canal", "Señal", "Seguridad", "Fabricante"
        ]
        
        print(tabulate(
            table_data,
            headers=headers,
            tablefmt="grid",
            maxcolwidths=[3, 25, 17, 10, 20, 15, 15]
        ))
        print()
    
    def _create_signal_bar(self, percentage: int) -> str:
        """Crea una barra visual de señal"""
        if percentage >= 80:
            color = Fore.GREEN
            bars = "█" * 10
        elif percentage >= 60:
            color = Fore.GREEN
            bars = "█" * 8 + "░" * 2
        elif percentage >= 40:
            color = Fore.YELLOW
            bars = "█" * 6 + "░" * 4
        elif percentage >= 20:
            color = Fore.YELLOW
            bars = "█" * 4 + "░" * 6
        else:
            color = Fore.RED
            bars = "█" * 2 + "░" * 8
        
        return f"{color}{bars}{Style.RESET_ALL}"
    
    def _get_security_color(self, security: str) -> str:
        """Devuelve color según tipo de seguridad"""
        if 'WPA3' in security:
            return Fore.GREEN
        elif 'WPA2' in security:
            return Fore.CYAN
        elif 'WPA' in security:
            return Fore.YELLOW
        elif 'WEP' in security:
            return Fore.MAGENTA
        elif 'Abierta' in security:
            return Fore.RED
        else:
            return Fore.WHITE
    
    def display_channel_analysis(self):
        """Muestra el análisis de canales"""
        channel_analysis = self.analysis.get('channel_analysis', {})
        if not channel_analysis:
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 ANÁLISIS DE CANALES")
        print("-" * 60)
        
        # Mostrar canales congestionados
        congested = channel_analysis.get('congested_channels', {})
        if congested:
            print(f"{Fore.YELLOW}📶 Canales congestionados:")
            for channel, data in list(congested.items())[:5]:
                level_color = {
                    'Alta': Fore.RED,
                    'Media': Fore.YELLOW,
                    'Baja': Fore.GREEN
                }.get(data['congestion_level'], Fore.WHITE)
                
                bar = "█" * min(data['network_count'], 10)
                print(f"  Canal {channel} ({data['band']}): {bar} {data['network_count']} redes "
                      f"{level_color}({data['congestion_level']})")
        else:
            print(f"{Fore.GREEN}✅ No se detectó congestión significativa")
        
        # Mostrar canales recomendados
        recommended = channel_analysis.get('recommended_channels', {})
        if recommended:
            print(f"\n{Fore.GREEN}✅ Canales recomendados:")
            for band, channels in recommended.items():
                if channels:
                    print(f"  {band}: {', '.join(map(str, channels[:3]))}")
    
    def display_recommendations(self):
        """Muestra las recomendaciones generadas"""
        recommendations = self.analysis.get('recommendations', [])
        if not recommendations:
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🎯 RECOMENDACIONES")
        print("-" * 60)
        
        for rec in recommendations:
            if rec.startswith("📡"):
                print(f"{Fore.YELLOW}{rec}")
            elif rec.startswith("🔓") or rec.startswith("🔒"):
                print(f"{Fore.RED}{rec}")
            elif rec.startswith("✅") or rec.startswith("🛡️"):
                print(f"{Fore.GREEN}{rec}")
            elif rec.startswith("📶"):
                print(f"{Fore.BLUE}{rec}")
            elif rec.startswith("⭐"):
                print(f"{Fore.MAGENTA}{Style.BRIGHT}{rec}")
            else:
                print(f"{Fore.WHITE}{rec}")
    
    def display_interface_info(self, interface_info: Dict):
        """Muestra información de la interfaz WiFi"""
        if not interface_info:
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🔧 INFORMACIÓN DE INTERFAZ")
        print("-" * 60)
        
        # Formatear y mostrar
        info_items = {
            'Interface': interface_info.get('interface', 'N/A'),
            'Mode': interface_info.get('mode', 'N/A'),
            'ESSID': interface_info.get('essid', 'N/A'),
            'Bitrate': interface_info.get('bitrate', 'N/A'),
            'Tx-Power': interface_info.get('tx_power', 'N/A'),
            'Channel': interface_info.get('channel', 'N/A'),
            'Signal': interface_info.get('signal', 'N/A')
        }
        
        # Mostrar en formato clave-valor
        for key, value in info_items.items():
            if value != 'N/A':
                print(f"  {Fore.GREEN}{key}: {Fore.WHITE}{value}")
    
    def display_statistics(self, stats: Dict):
        """Muestra estadísticas de las redes"""
        if not stats:
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📈 ESTADÍSTICAS DE RED")
        print("-" * 60)
        
        # Mostrar estadísticas principales
        print(f"  {Fore.GREEN}Total redes: {Fore.WHITE}{stats.get('total_networks', 0)}")
        print(f"  {Fore.RED}Redes abiertas: {Fore.WHITE}{stats.get('open_networks', 0)}")
        print(f"  {Fore.CYAN}Redes WPA2: {Fore.WHITE}{stats.get('wpa2_networks', 0)}")
        print(f"  {Fore.GREEN}Redes WPA3: {Fore.WHITE}{stats.get('wpa3_networks', 0)}")
        
        # Top fabricantes
        by_vendor = stats.get('by_vendor', {})
        if by_vendor:
            print(f"\n  {Fore.YELLOW}Top fabricantes:")
            for vendor, count in list(by_vendor.items())[:5]:
                print(f"    {vendor}: {count} red(es)")
    
    def display_summary(self, networks: List[Dict], interface_info: Dict, stats: Dict):
        """
        Muestra un resumen completo de toda la información
        
        Args:
            networks: Lista de redes
            interface_info: Información de la interfaz
            stats: Estadísticas
        """
        # Limpiar pantalla
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
        # Header
        self.display_header()
        
        # Redes
        self.display_networks(networks)
        
        # Análisis de canales
        self.display_channel_analysis()
        
        # Recomendaciones
        self.display_recommendations()
        
        # Estadísticas
        self.display_statistics(stats)
        
        # Información de interfaz
        self.display_interface_info(interface_info)
        
        # Footer
        print("\n" + "=" * self.terminal_width)
        print(f"{Fore.CYAN}🔍 Escaneo completado - {len(networks)} redes encontradas")
        print("=" * self.terminal_width + "\n")
    
    def display_simple(self, networks: List[Dict]):
        """
        Muestra una versión simple de la información (solo redes)
        
        Args:
            networks: Lista de redes
        """
        self.display_header()
        self.display_networks(networks)
