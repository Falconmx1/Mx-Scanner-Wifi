"""
Módulo de análisis de redes WiFi
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import statistics

class NetworkAnalyzer:
    """Clase para analizar redes WiFi y generar recomendaciones"""
    
    def __init__(self, networks: List[Dict]):
        self.networks = networks
        self.channel_usage = defaultdict(list)
        self._analyze_channels()
    
    def _analyze_channels(self):
        """Analiza el uso de canales"""
        for network in self.networks:
            if network.get('channel') and network['channel'].isdigit():
                channel = int(network['channel'])
                self.channel_usage[channel].append(network)
    
    def analyze_all(self) -> Dict:
        """
        Realiza un análisis completo de todas las redes
        
        Returns:
            Dict: Análisis completo con recomendaciones
        """
        analysis = {
            'total_networks': len(self.networks),
            'by_security': self._analyze_security(),
            'by_band': self._analyze_bands(),
            'signal_stats': self._analyze_signal(),
            'channel_analysis': self._analyze_channel_congestion(),
            'best_networks': self._find_best_networks(),
            'recommendations': []
        }
        
        # Generar recomendaciones
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_security(self) -> Dict:
        """Analiza los tipos de seguridad"""
        security_types = defaultdict(int)
        for network in self.networks:
            sec = network.get('security', 'Desconocida')
            security_types[sec] += 1
        return dict(security_types)
    
    def _analyze_bands(self) -> Dict:
        """Analiza el uso de bandas"""
        bands = defaultdict(int)
        for network in self.networks:
            band = network.get('band', 'Desconocida')
            bands[band] += 1
        return dict(bands)
    
    def _analyze_signal(self) -> Dict:
        """Analiza estadísticas de señal"""
        signals = []
        for network in self.networks:
            signal = network.get('signal', {})
            if signal.get('percentage'):
                signals.append(signal['percentage'])
        
        if signals:
            return {
                'avg': statistics.mean(signals),
                'min': min(signals),
                'max': max(signals),
                'median': statistics.median(signals)
            }
        return {}
    
    def _analyze_channel_congestion(self) -> Dict:
        """Analiza la congestión de canales"""
        congestion = {}
        
        for channel, networks in self.channel_usage.items():
            band = self._get_band_from_channel(channel)
            # Calcular nivel de congestión basado en número de redes y su señal
            avg_signal = statistics.mean([n.get('signal', {}).get('percentage', 0) for n in networks])
            
            congestion[channel] = {
                'network_count': len(networks),
                'band': band,
                'avg_signal': avg_signal,
                'congestion_level': self._get_congestion_level(len(networks))
            }
        
        # Ordenar por congestión
        sorted_congestion = dict(sorted(
            congestion.items(),
            key=lambda x: (x[1]['network_count'], -x[1]['avg_signal']),
            reverse=True
        ))
        
        # Encontrar canales recomendados
        recommended = self._get_recommended_channels(sorted_congestion)
        
        return {
            'congested_channels': sorted_congestion,
            'recommended_channels': recommended
        }
    
    def _get_band_from_channel(self, channel: int) -> str:
        """Determina la banda según el canal"""
        if 1 <= channel <= 14:
            return '2.4 GHz'
        elif 36 <= channel <= 165:
            return '5 GHz'
        return 'Desconocida'
    
    def _get_congestion_level(self, network_count: int) -> str:
        """Determina el nivel de congestión"""
        if network_count >= 5:
            return 'Alta'
        elif network_count >= 3:
            return 'Media'
        else:
            return 'Baja'
    
    def _get_recommended_channels(self, congestion: Dict) -> Dict:
        """Sugiere canales recomendados por banda"""
        recommended = {
            '2.4 GHz': [],
            '5 GHz': []
        }
        
        # Canales recomendados para 2.4 GHz (1, 6, 11 son los principales no superpuestos)
        for channel in [1, 6, 11]:
            if channel in congestion:
                if congestion[channel]['network_count'] <= 2:
                    recommended['2.4 GHz'].append(channel)
            else:
                recommended['2.4 GHz'].append(channel)
        
        # Para 5 GHz, sugerir canales menos usados entre 36-48 y 149-165
        for channel in [36, 40, 44, 48, 149, 153, 157, 161]:
            if channel in congestion:
                if congestion[channel]['network_count'] <= 2:
                    recommended['5 GHz'].append(channel)
            else:
                recommended['5 GHz'].append(channel)
        
        return recommended
    
    def _find_best_networks(self) -> Dict:
        """
        Encuentra las mejores redes según diferentes criterios
        
        Returns:
            Dict: Mejores redes por señal y seguridad
        """
        best = {
            'by_signal': None,
            'by_security': None,
            'best_overall': None
        }
        
        # Mejor por señal
        valid_networks = [n for n in self.networks if n.get('signal', {}).get('percentage') is not None]
        if valid_networks:
            best['by_signal'] = max(valid_networks, key=lambda x: x['signal']['percentage'])
        
        # Mejor por seguridad (priorizar WPA3 > WPA2 > WPA > WEP > Abierta)
        security_priority = {
            'WPA3': 5,
            'WPA2': 4,
            'WPA': 3,
            'WEP': 2,
            'Abierta': 1
        }
        
        if self.networks:
            best['by_security'] = max(
                self.networks,
                key=lambda x: security_priority.get(x.get('security', ''), 0)
            )
            
            # Mejor general (combinación de señal y seguridad)
            best['best_overall'] = max(
                self.networks,
                key=lambda x: (
                    security_priority.get(x.get('security', ''), 0) * 0.6 + 
                    (x.get('signal', {}).get('percentage', 0) / 100) * 0.4
                )
            )
        
        return best
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Genera recomendaciones basadas en el análisis
        
        Returns:
            List[str]: Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendación de canal
        if analysis['channel_analysis']['recommended_channels']['2.4 GHz']:
            rec_channel = analysis['channel_analysis']['recommended_channels']['2.4 GHz'][0]
            recommendations.append(f"📡 Canal recomendado para 2.4 GHz: {rec_channel}")
        else:
            recommendations.append("📡 Todos los canales 2.4 GHz están congestionados")
        
        if analysis['channel_analysis']['recommended_channels']['5 GHz']:
            rec_channel_5 = analysis['channel_analysis']['recommended_channels']['5 GHz'][0]
            recommendations.append(f"📡 Canal recomendado para 5 GHz: {rec_channel_5}")
        
        # Recomendación de seguridad
        security_types = analysis['by_security']
        if 'Abierta' in security_types and security_types['Abierta'] > 0:
            recommendations.append("🔓 Hay redes abiertas detectadas - evita conectarte a ellas")
        
        if 'WPA3' in security_types:
            recommendations.append("✅ Redes con WPA3 disponibles - son la opción más segura")
        elif 'WPA2' in security_types:
            recommendations.append("🛡️ WPA2 disponible - asegúrate de usar contraseñas seguras")
        
        # Recomendación de señal
        signal_stats = analysis.get('signal_stats', {})
        if signal_stats:
            if signal_stats.get('avg', 0) < 50:
                recommendations.append("📶 Señal promedio baja - considera usar un repetidor WiFi")
            elif signal_stats.get('avg', 0) > 70:
                recommendations.append("📶 Buena señal promedio - entorno WiFi saludable")
        
        # Recomendaciones específicas
        if analysis['best_networks']['best_overall']:
            best = analysis['best_networks']['best_overall']
            recommendations.append(
                f"⭐ Mejor red general: {best.get('ssid', 'Desconocida')} "
                f"(Señal: {best.get('signal', {}).get('percentage', 0)}%, "
                f"Seguridad: {best.get('security', 'Desconocida')})"
            )
        
        return recommendations
    
    def get_network_statistics(self) -> Dict:
        """
        Obtiene estadísticas detalladas de las redes
        
        Returns:
            Dict: Estadísticas completas
        """
        stats = {
            'total_networks': len(self.networks),
            'open_networks': len([n for n in self.networks if n.get('security') == 'Abierta']),
            'wpa2_networks': len([n for n in self.networks if 'WPA2' in n.get('security', '')]),
            'wpa3_networks': len([n for n in self.networks if 'WPA3' in n.get('security', '')]),
            'by_channel': {},
            'by_vendor': {}
        }
        
        # Contar por canal
        for network in self.networks:
            channel = network.get('channel', '0')
            stats['by_channel'][channel] = stats['by_channel'].get(channel, 0) + 1
        
        # Contar por fabricante
        for network in self.networks:
            vendor = network.get('vendor', 'Desconocido')
            stats['by_vendor'][vendor] = stats['by_vendor'].get(vendor, 0) + 1
        
        # Ordenar por cantidad
        stats['by_channel'] = dict(sorted(
            stats['by_channel'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        stats['by_vendor'] = dict(sorted(
            stats['by_vendor'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])  # Top 10 fabricantes
        
        return stats
