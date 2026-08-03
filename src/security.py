"""
Módulo de análisis de seguridad WiFi
"""

from typing import Dict, List, Tuple
import hashlib
import re
from datetime import datetime

class SecurityAnalyzer:
    """Clase para analizar la seguridad de redes WiFi"""
    
    def __init__(self, networks: List[Dict]):
        self.networks = networks
    
    def analyze_security(self) -> Dict:
        """
        Realiza un análisis completo de seguridad
        
        Returns:
            Dict: Análisis de seguridad detallado
        """
        security_analysis = {
            'summary': self._get_security_summary(),
            'vulnerabilities': self._find_vulnerabilities(),
            'recommendations': self._get_security_recommendations(),
            'security_score': self._calculate_security_score()
        }
        
        return security_analysis
    
    def _get_security_summary(self) -> Dict:
        """Resumen de seguridad de las redes"""
        summary = {
            'total_networks': len(self.networks),
            'secure_networks': 0,
            'insecure_networks': 0,
            'encryption_types': {},
            'weak_passwords': []
        }
        
        for network in self.networks:
            security = network.get('security', 'Desconocida')
            
            # Clasificar seguridad
            if security in ['WPA3-Personal', 'WPA3-Enterprise']:
                summary['secure_networks'] += 1
                summary['encryption_types']['WPA3'] = summary['encryption_types'].get('WPA3', 0) + 1
            elif 'WPA2' in security:
                summary['secure_networks'] += 1
                summary['encryption_types']['WPA2'] = summary['encryption_types'].get('WPA2', 0) + 1
            elif 'WPA' in security:
                summary['secure_networks'] += 1
                summary['encryption_types']['WPA'] = summary['encryption_types'].get('WPA', 0) + 1
            elif 'WEP' in security:
                summary['insecure_networks'] += 1
                summary['encryption_types']['WEP'] = summary['encryption_types'].get('WEP', 0) + 1
            elif 'Abierta' in security:
                summary['insecure_networks'] += 1
                summary['encryption_types']['Open'] = summary['encryption_types'].get('Open', 0) + 1
            else:
                summary['encryption_types'][security] = summary['encryption_types'].get(security, 0) + 1
        
        return summary
    
    def _find_vulnerabilities(self) -> List[Dict]:
        """Encuentra vulnerabilidades en las redes"""
        vulnerabilities = []
        
        for network in self.networks:
            ssid = network.get('ssid', 'Desconocida')
            security = network.get('security', '')
            
            # Redes abiertas
            if security == 'Abierta':
                vulnerabilities.append({
                    'network': ssid,
                    'type': 'Open Network',
                    'severity': 'Alta',
                    'description': f'Red "{ssid}" está completamente abierta - sin encriptación',
                    'bssid': network.get('bssid', 'N/A')
                })
            
            # WEP es obsoleto
            elif 'WEP' in security:
                vulnerabilities.append({
                    'network': ssid,
                    'type': 'WEP Encryption',
                    'severity': 'Alta',
                    'description': f'Red "{ssid}" usa WEP - cifrado obsoleto y vulnerable',
                    'bssid': network.get('bssid', 'N/A')
                })
            
            # WPA inseguro
            elif 'WPA' in security and 'WPA2' not in security:
                vulnerabilities.append({
                    'network': ssid,
                    'type': 'WPA Legacy',
                    'severity': 'Media',
                    'description': f'Red "{ssid}" usa WPA (no WPA2/WPA3) - vulnerable a ataques KRACK',
                    'bssid': network.get('bssid', 'N/A')
                })
            
            # WPA2 con malas configuraciones
            elif 'WPA2' in security and 'TKIP' in security:
                vulnerabilities.append({
                    'network': ssid,
                    'type': 'WPA2-TKIP',
                    'severity': 'Media',
                    'description': f'Red "{ssid}" usa WPA2 con TKIP - menos seguro que AES',
                    'bssid': network.get('bssid', 'N/A')
                })
        
        return vulnerabilities
    
    def _get_security_recommendations(self) -> List[str]:
        """Genera recomendaciones de seguridad"""
        recommendations = []
        
        # Analizar redes para dar recomendaciones
        if self.networks:
            # Recomendaciones generales
            recommendations.append("🔒 Usa WPA3 cuando sea posible para máxima seguridad")
            recommendations.append("🔑 Usa contraseñas de al menos 12 caracteres con mayúsculas, minúsculas, números y símbolos")
            recommendations.append("🔄 Cambia la contraseña del WiFi cada 3-6 meses")
            
            # Detectar redes inseguras
            for network in self.networks:
                security = network.get('security', '')
                if security == 'Abierta':
                    recommendations.append(f"⚠️ La red '{network.get('ssid', '')}' está abierta - considera evitar conectarte")
                elif 'WEP' in security:
                    recommendations.append(f"⚠️ La red '{network.get('ssid', '')}' usa WEP obsoleto - evita conectarte")
        
        return recommendations
    
    def _calculate_security_score(self) -> Dict:
        """
        Calcula un puntaje de seguridad para el entorno
        
        Returns:
            Dict: Puntaje de seguridad
        """
        total = len(self.networks)
        if total == 0:
            return {'score': 0, 'level': 'Sin redes', 'details': {}}
        
        # Ponderar tipos de seguridad
        scores = {
            'WPA3': 100,
            'WPA2': 80,
            'WPA': 60,
            'WEP': 20,
            'Open': 0,
            'Unknown': 50
        }
        
        total_score = 0
        details = {}
        
        for network in self.networks:
            security = network.get('security', 'Unknown')
            
            # Determinar tipo base
            base_type = 'Unknown'
            if 'WPA3' in security:
                base_type = 'WPA3'
            elif 'WPA2' in security:
                base_type = 'WPA2'
            elif 'WPA' in security:
                base_type = 'WPA'
            elif 'WEP' in security:
                base_type = 'WEP'
            elif 'Abierta' in security or 'Open' in security:
                base_type = 'Open'
            
            score = scores.get(base_type, 50)
            total_score += score
            details[security] = details.get(security, 0) + 1
        
        avg_score = total_score / total
        
        # Determinar nivel
        if avg_score >= 80:
            level = 'Alto'
            color = '🟢'
        elif avg_score >= 60:
            level = 'Medio'
            color = '🟡'
        elif avg_score >= 40:
            level = 'Bajo'
            color = '🟠'
        else:
            level = 'Crítico'
            color = '🔴'
        
        return {
            'score': round(avg_score, 1),
            'level': level,
            'color': color,
            'details': details
        }
    
    def check_password_strength(self, password: str) -> Dict:
        """
        Verifica la fortaleza de una contraseña
        
        Args:
            password: Contraseña a evaluar
            
        Returns:
            Dict: Análisis de fortaleza
        """
        score = 0
        feedback = []
        
        # Longitud
        if len(password) >= 12:
            score += 2
            feedback.append("✅ Longitud excelente (12+ caracteres)")
        elif len(password) >= 8:
            score += 1
            feedback.append("✅ Longitud aceptable (8-11 caracteres)")
        else:
            feedback.append("❌ Longitud insuficiente (mínimo 8 caracteres)")
        
        # Complejidad
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if has_upper and has_lower and has_digit and has_special:
            score += 3
            feedback.append("✅ Excelente complejidad (mayúsculas, minúsculas, números, especiales)")
        elif (has_upper and has_lower and has_digit) or (has_upper and has_lower and has_special):
            score += 2
            feedback.append("✅ Buena complejidad (3 de 4 tipos)")
        elif has_upper or has_lower:
            score += 1
            feedback.append("⚠️ Complejidad básica (solo 1 tipo de caracteres)")
        else:
            feedback.append("❌ Mala complejidad (solo un tipo de caracteres)")
        
        # Entropía aproximada
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32
        
        if charset_size > 0:
            entropy = len(password) * (charset_size.bit_length())
        else:
            entropy = 0
        
        # Nivel
        if score >= 5:
            level = 'Excelente'
        elif score >= 3:
            level = 'Fuerte'
        elif score >= 2:
            level = 'Débil'
        else:
            level = 'Muy Débil'
        
        return {
            'score': score,
            'max_score': 6,
            'level': level,
            'entropy': entropy,
            'feedback': feedback
        }
    
    def get_network_security_ranking(self) -> List[Dict]:
        """
        Ordena las redes por nivel de seguridad
        
        Returns:
            List[Dict]: Redes ordenadas por seguridad
        """
        ranking = []
        
        security_order = {
            'WPA3': 5,
            'WPA2': 4,
            'WPA': 3,
            'WEP': 2,
            'Abierta': 1
        }
        
        for network in self.networks:
            security = network.get('security', 'Unknown')
            
            # Determinar tipo base
            base_type = 'Unknown'
            if 'WPA3' in security:
                base_type = 'WPA3'
            elif 'WPA2' in security:
                base_type = 'WPA2'
            elif 'WPA' in security:
                base_type = 'WPA'
            elif 'WEP' in security:
                base_type = 'WEP'
            elif 'Abierta' in security or 'Open' in security:
                base_type = 'Abierta'
            
            security_score = security_order.get(base_type, 1)
            
            ranking.append({
                'ssid': network.get('ssid', 'Unknown'),
                'bssid': network.get('bssid', 'N/A'),
                'security': security,
                'security_score': security_score,
                'signal': network.get('signal', {}).get('percentage', 0),
                'vendor': network.get('vendor', 'Desconocido')
            })
        
        # Ordenar por seguridad (descendente) y señal (descendente)
        ranking.sort(key=lambda x: (-x['security_score'], -x['signal']))
        
        return ranking
