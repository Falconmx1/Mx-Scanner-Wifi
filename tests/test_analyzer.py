"""
Pruebas unitarias para el módulo analyzer.py
"""

import unittest
import sys
import os
from typing import List, Dict

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import NetworkAnalyzer

class TestNetworkAnalyzer(unittest.TestCase):
    """Pruebas para la clase NetworkAnalyzer"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.sample_networks = self._create_sample_networks()
        self.analyzer = NetworkAnalyzer(self.sample_networks)
    
    def _create_sample_networks(self) -> List[Dict]:
        """Crea redes de ejemplo para pruebas"""
        return [
            {
                'ssid': 'RedSegura',
                'bssid': '00:1A:2B:3C:4D:5E',
                'vendor': 'TP-Link',
                'channel': '6',
                'band': '2.4 GHz',
                'frequency': 2437,
                'security': 'WPA3-Personal',
                'signal': {'percentage': 85, 'dbm': -45, 'quality': 'Excelente'}
            },
            {
                'ssid': 'RedAbierta',
                'bssid': '00:1C:10:11:22:33',
                'vendor': 'Netgear',
                'channel': '1',
                'band': '2.4 GHz',
                'frequency': 2412,
                'security': 'Abierta',
                'signal': {'percentage': 60, 'dbm': -65, 'quality': 'Buena'}
            },
            {
                'ssid': 'RedWPA2',
                'bssid': '00:14:6C:44:55:66',
                'vendor': 'Cisco',
                'channel': '36',
                'band': '5 GHz',
                'frequency': 5180,
                'security': 'WPA2-Personal',
                'signal': {'percentage': 40, 'dbm': -75, 'quality': 'Regular'}
            },
            {
                'ssid': 'RedWEP',
                'bssid': '00:1D:AA:77:88:99',
                'vendor': 'D-Link',
                'channel': '11',
                'band': '2.4 GHz',
                'frequency': 2462,
                'security': 'WEP',
                'signal': {'percentage': 25, 'dbm': -85, 'quality': 'Mala'}
            }
        ]
    
    def test_initialization(self):
        """Prueba la inicialización del analizador"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.networks), 4)
        self.assertEqual(len(self.analyzer.channel_usage), 4)
    
    def test_analyze_security(self):
        """Prueba el análisis de seguridad"""
        security = self.analyzer._analyze_security()
        
        self.assertIn('WPA3-Personal', security)
        self.assertIn('Abierta', security)
        self.assertIn('WPA2-Personal', security)
        self.assertIn('WEP', security)
        
        self.assertEqual(security['WPA3-Personal'], 1)
        self.assertEqual(security['Abierta'], 1)
        self.assertEqual(security['WPA2-Personal'], 1)
        self.assertEqual(security['WEP'], 1)
    
    def test_analyze_bands(self):
        """Prueba el análisis de bandas"""
        bands = self.analyzer._analyze_bands()
        
        self.assertEqual(bands['2.4 GHz'], 3)  # 3 redes en 2.4 GHz
        self.assertEqual(bands['5 GHz'], 1)    # 1 red en 5 GHz
    
    def test_analyze_signal(self):
        """Prueba el análisis de señales"""
        signal_stats = self.analyzer._analyze_signal()
        
        self.assertIn('avg', signal_stats)
        self.assertIn('min', signal_stats)
        self.assertIn('max', signal_stats)
        self.assertIn('median', signal_stats)
        
        # Valores esperados: [85, 60, 40, 25]
        self.assertEqual(signal_stats['min'], 25)
        self.assertEqual(signal_stats['max'], 85)
        self.assertEqual(signal_stats['avg'], 52.5)
        self.assertEqual(signal_stats['median'], 50)
    
    def test_analyze_channel_congestion(self):
        """Prueba el análisis de congestión de canales"""
        congestion = self.analyzer._analyze_channel_congestion()
        
        self.assertIn('congested_channels', congestion)
        self.assertIn('recommended_channels', congestion)
        
        # Verificar canales
        channels = congestion['congested_channels']
        self.assertIn(6, channels)  # Canal 6 tiene 1 red
        self.assertIn(1, channels)  # Canal 1 tiene 1 red
        self.assertIn(36, channels) # Canal 36 tiene 1 red
        self.assertIn(11, channels) # Canal 11 tiene 1 red
    
    def test_get_congestion_level(self):
        """Prueba la determinación del nivel de congestión"""
        self.assertEqual(self.analyzer._get_congestion_level(0), 'Baja')
        self.assertEqual(self.analyzer._get_congestion_level(1), 'Baja')
        self.assertEqual(self.analyzer._get_congestion_level(2), 'Baja')
        self.assertEqual(self.analyzer._get_congestion_level(3), 'Media')
        self.assertEqual(self.analyzer._get_congestion_level(4), 'Media')
        self.assertEqual(self.analyzer._get_congestion_level(5), 'Alta')
        self.assertEqual(self.analyzer._get_congestion_level(10), 'Alta')
    
    def test_find_best_networks(self):
        """Prueba la identificación de mejores redes"""
        best = self.analyzer._find_best_networks()
        
        # Mejor por señal debe ser RedSegura (85%)
        self.assertEqual(best['by_signal']['ssid'], 'RedSegura')
        
        # Mejor por seguridad debe ser RedSegura (WPA3)
        self.assertEqual(best['by_security']['ssid'], 'RedSegura')
        
        # Mejor general debe ser RedSegura (WPA3 + alta señal)
        self.assertEqual(best['best_overall']['ssid'], 'RedSegura')
    
    def test_generate_recommendations(self):
        """Prueba la generación de recomendaciones"""
        analysis = self.analyzer.analyze_all()
        recommendations = analysis['recommendations']
        
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)
        
        # Verificar que hay recomendaciones específicas
        has_security_recommendation = any('seguridad' in rec.lower() for rec in recommendations)
        has_channel_recommendation = any('canal' in rec.lower() for rec in recommendations)
        
        self.assertTrue(has_security_recommendation)
        self.assertTrue(has_channel_recommendation)
    
    def test_get_network_statistics(self):
        """Prueba la obtención de estadísticas de red"""
        stats = self.analyzer.get_network_statistics()
        
        self.assertEqual(stats['total_networks'], 4)
        self.assertEqual(stats['open_networks'], 1)
        self.assertEqual(stats['wpa2_networks'], 1)
        self.assertEqual(stats['wpa3_networks'], 1)
        
        # Verificar estadísticas por canal
        self.assertEqual(len(stats['by_channel']), 4)
        for channel in ['1', '6', '11', '36']:
            self.assertIn(channel, stats['by_channel'])
            self.assertEqual(stats['by_channel'][channel], 1)
        
        # Verificar estadísticas por fabricante
        self.assertEqual(len(stats['by_vendor']), 4)
        self.assertIn('TP-Link', stats['by_vendor'])
        self.assertIn('Netgear', stats['by_vendor'])
    
    def test_analyze_all(self):
        """Prueba el análisis completo"""
        analysis = self.analyzer.analyze_all()
        
        # Verificar que todos los campos existen
        required_fields = [
            'total_networks', 'by_security', 'by_band',
            'signal_stats', 'channel_analysis', 'best_networks',
            'recommendations'
        ]
        
        for field in required_fields:
            self.assertIn(field, analysis)
        
        # Verificar valores
        self.assertEqual(analysis['total_networks'], 4)
        self.assertIsInstance(analysis['recommendations'], list)

class TestNetworkAnalyzerEdgeCases(unittest.TestCase):
    """Pruebas de casos límite para NetworkAnalyzer"""
    
    def test_empty_networks(self):
        """Prueba con lista vacía de redes"""
        analyzer = NetworkAnalyzer([])
        analysis = analyzer.analyze_all()
        
        self.assertEqual(analysis['total_networks'], 0)
        self.assertEqual(len(analysis['recommendations']), 0)
        self.assertEqual(analysis['by_security'], {})
        self.assertEqual(analysis['by_band'], {})
    
    def test_networks_without_signal(self):
        """Prueba con redes sin información de señal"""
        networks = [
            {'ssid': 'Red1', 'security': 'WPA2', 'channel': '6'},
            {'ssid': 'Red2', 'security': 'Abierta', 'channel': '11'}
        ]
        
        analyzer = NetworkAnalyzer(networks)
        analysis = analyzer.analyze_all()
        
        # No debe haber estadísticas de señal
        self.assertEqual(analysis['signal_stats'], {})
        
        # Pero debe haber análisis de seguridad
        self.assertIn('WPA2', analysis['by_security'])
        self.assertIn('Abierta', analysis['by_security'])
    
    def test_networks_with_invalid_channel(self):
        """Prueba con canales inválidos"""
        networks = [
            {'ssid': 'Red1', 'channel': 'invalid', 'signal': {'percentage': 50}},
            {'ssid': 'Red2', 'channel': '999', 'signal': {'percentage': 60}}
        ]
        
        analyzer = NetworkAnalyzer(networks)
        analysis = analyzer.analyze_all()
        
        # Los canales inválidos deben ser ignorados en el análisis
        self.assertEqual(len(analysis['channel_analysis']['congested_channels']), 0)
    
    def test_networks_with_all_security_types(self):
        """Prueba con todos los tipos de seguridad"""
        networks = [
            {'ssid': 'WPA3', 'security': 'WPA3-Enterprise'},
            {'ssid': 'WPA2', 'security': 'WPA2-Enterprise'},
            {'ssid': 'WPA', 'security': 'WPA-Personal'},
            {'ssid': 'WEP', 'security': 'WEP'},
            {'ssid': 'Open', 'security': 'Abierta'},
            {'ssid': 'Unknown', 'security': 'Unknown'}
        ]
        
        analyzer = NetworkAnalyzer(networks)
        security = analyzer._analyze_security()
        
        self.assertEqual(len(security), 6)
        self.assertEqual(security['WPA3-Enterprise'], 1)
        self.assertEqual(security['WPA2-Enterprise'], 1)
        self.assertEqual(security['WPA-Personal'], 1)
        self.assertEqual(security['WEP'], 1)
        self.assertEqual(security['Abierta'], 1)
        self.assertEqual(security['Unknown'], 1)

if __name__ == '__main__':
    unittest.main()
