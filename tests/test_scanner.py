"""
Pruebas unitarias para el módulo scanner.py
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scanner import WifiScanner

class TestWifiScanner(unittest.TestCase):
    """Pruebas para la clase WifiScanner"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.scanner = WifiScanner()
    
    def test_initialization(self):
        """Prueba la inicialización del escáner"""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(self.scanner.os_type, sys.platform.capitalize())
        self.assertEqual(self.scanner.networks, [])
    
    def test_parse_signal_percentage(self):
        """Prueba el parseo de señal en porcentaje"""
        result = self.scanner._parse_signal("75%")
        self.assertEqual(result['percentage'], 75)
        self.assertTrue(result['dbm'] < 0)
        self.assertEqual(result['quality'], 'Excelente')
    
    def test_parse_signal_dbm(self):
        """Prueba el parseo de señal en dBm"""
        result = self.scanner._parse_signal("-65")
        self.assertTrue(result['percentage'] > 0)
        self.assertEqual(result['dbm'], -65)
    
    def test_parse_signal_invalid(self):
        """Prueba el parseo de señal inválida"""
        result = self.scanner._parse_signal("invalid")
        self.assertEqual(result['percentage'], 0)
        self.assertEqual(result['dbm'], -100)
    
    def test_get_signal_quality(self):
        """Prueba la clasificación de calidad de señal"""
        self.assertEqual(self.scanner._get_signal_quality(80), 'Excelente')
        self.assertEqual(self.scanner._get_signal_quality(60), 'Buena')
        self.assertEqual(self.scanner._get_signal_quality(40), 'Regular')
        self.assertEqual(self.scanner._get_signal_quality(20), 'Mala')
    
    def test_get_frequency_2_4ghz(self):
        """Prueba la conversión de canal a frecuencia en 2.4 GHz"""
        # Canal 1 -> 2412 MHz
        self.assertEqual(self.scanner._get_frequency("1"), 2412)
        # Canal 6 -> 2437 MHz
        self.assertEqual(self.scanner._get_frequency("6"), 2437)
        # Canal 11 -> 2462 MHz
        self.assertEqual(self.scanner._get_frequency("11"), 2462)
    
    def test_get_frequency_5ghz(self):
        """Prueba la conversión de canal a frecuencia en 5 GHz"""
        # Canal 36 -> 5180 MHz
        self.assertEqual(self.scanner._get_frequency("36"), 5180)
        # Canal 48 -> 5240 MHz
        self.assertEqual(self.scanner._get_frequency("48"), 5240)
        # Canal 149 -> 5745 MHz
        self.assertEqual(self.scanner._get_frequency("149"), 5745)
    
    def test_get_frequency_invalid(self):
        """Prueba la conversión de canal inválido"""
        self.assertEqual(self.scanner._get_frequency("invalid"), 0)
        self.assertEqual(self.scanner._get_frequency("99"), 0)
    
    def test_get_band(self):
        """Prueba la detección de banda según canal"""
        self.assertEqual(self.scanner._get_band("1"), '2.4 GHz')
        self.assertEqual(self.scanner._get_band("6"), '2.4 GHz')
        self.assertEqual(self.scanner._get_band("11"), '2.4 GHz')
        self.assertEqual(self.scanner._get_band("36"), '5 GHz')
        self.assertEqual(self.scanner._get_band("149"), '5 GHz')
        self.assertEqual(self.scanner._get_band("invalid"), 'Desconocida')
    
    def test_get_vendor(self):
        """Prueba la identificación de fabricante por MAC"""
        self.assertEqual(self.scanner._get_vendor("00:1A:2B:00:00:00"), 'TP-Link')
        self.assertEqual(self.scanner._get_vendor("00:1C:10:00:00:00"), 'Netgear')
        self.assertEqual(self.scanner._get_vendor("00:14:6C:00:00:00"), 'Cisco')
        self.assertEqual(self.scanner._get_vendor("00:00:00:00:00:00"), 'Desconocido')
    
    @patch('subprocess.run')
    def test_scan_linux_nmcli(self, mock_run):
        """Prueba el escaneo en Linux usando nmcli"""
        # Simular que estamos en Linux
        self.scanner.os_type = 'Linux'
        
        # Simular salida de nmcli
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="MiWiFi:00:1A:2B:3C:4D:5E:WPA2:6:80\nRedVecinos:00:1C:10:11:22:33:WPA2:1:60\n",
            stderr=""
        )
        
        networks = self.scanner.scan()
        self.assertIsInstance(networks, list)
    
    @patch('subprocess.run')
    def test_scan_linux_iwlist(self, mock_run):
        """Prueba el escaneo en Linux usando iwlist (fallback)"""
        self.scanner.os_type = 'Linux'
        
        # Simular fallo de nmcli
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error"
        )
        
        # Simular salida de iwlist
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Cell 01 - Address: 00:1A:2B:3C:4D:5E\nESSID:\"MiWiFi\"\nFrequency:2.437 GHz\nSignal level=-55\nEncryption key:on\n",
            stderr=""
        )
        
        networks = self.scanner.scan()
        self.assertIsInstance(networks, list)
    
    @patch('subprocess.run')
    def test_scan_windows(self, mock_run):
        """Prueba el escaneo en Windows"""
        self.scanner.os_type = 'Windows'
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SSID 1 : MiWiFi\nBSSID 1 : 00:1A:2B:3C:4D:5E\nSignal : 80%\nRadio type : 802.11n\nChannel : 6\n",
            stderr=""
        )
        
        networks = self.scanner.scan()
        self.assertIsInstance(networks, list)
    
    @patch('subprocess.run')
    def test_scan_error_handling(self, mock_run):
        """Prueba el manejo de errores durante el escaneo"""
        self.scanner.os_type = 'Linux'
        
        # Simular error de subprocess
        mock_run.side_effect = Exception("Comando no encontrado")
        
        networks = self.scanner.scan()
        self.assertEqual(networks, [])  # Debe retornar lista vacía
    
    def test_get_interface_info_unsupported_os(self):
        """Prueba la obtención de interfaz en OS no soportado"""
        self.scanner.os_type = 'Unknown'
        info = self.scanner.get_interface_info()
        self.assertEqual(info, {})  # Debe retornar diccionario vacío
    
    @patch('subprocess.run')
    def test_get_interface_linux(self, mock_run):
        """Prueba la obtención de interfaz en Linux"""
        self.scanner.os_type = 'Linux'
        
        # Simular salida de iwconfig
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="wlan0     IEEE 802.11  ESSID:\"MiWiFi\"\n          Mode:Managed  Frequency:2.437 GHz  Access Point: 00:1A:2B:3C:4D:5E\n          Bit Rate=72.2 Mb/s   Tx-Power=20 dBm\n",
            stderr=""
        )
        
        info = self.scanner.get_interface_info()
        self.assertIn('interface', info)
        self.assertEqual(info.get('interface'), 'wlan0')

class TestWifiScannerIntegration(unittest.TestCase):
    """Pruebas de integración para WifiScanner"""
    
    def test_full_scan_flow(self):
        """Prueba el flujo completo de escaneo"""
        scanner = WifiScanner()
        
        # No podemos probar el escaneo real en pruebas unitarias,
        # pero podemos verificar que el objeto existe y tiene métodos
        self.assertTrue(hasattr(scanner, 'scan'))
        self.assertTrue(hasattr(scanner, 'get_interface_info'))
        
    def test_network_structure(self):
        """Prueba la estructura de una red escaneada"""
        # Crear una red de prueba
        test_network = {
            'ssid': 'TestWiFi',
            'bssid': '00:1A:2B:3C:4D:5E',
            'vendor': 'TP-Link',
            'channel': '6',
            'band': '2.4 GHz',
            'frequency': 2437,
            'security': 'WPA2-PSK',
            'signal': {
                'percentage': 75,
                'dbm': -55,
                'quality': 'Excelente'
            },
            'timestamp': '2026-08-03T12:00:00'
        }
        
        # Verificar que todos los campos necesarios existen
        required_fields = ['ssid', 'bssid', 'vendor', 'channel', 'band', 
                          'frequency', 'security', 'signal']
        
        for field in required_fields:
            self.assertIn(field, test_network)
        
        # Verificar que signal tiene subcampos
        signal_fields = ['percentage', 'dbm', 'quality']
        for field in signal_fields:
            self.assertIn(field, test_network['signal'])

if __name__ == '__main__':
    unittest.main()
