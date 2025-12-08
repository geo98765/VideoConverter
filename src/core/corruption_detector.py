"""Módulo para detectar videos corruptos"""
import subprocess

class CorruptionDetector:
    """Detecta y analiza corrupción en videos"""
    
    @staticmethod
    def analyze_video(input_file):
        """Analiza un video en busca de corrupción"""
        try:
            cmd = [
                'ffmpeg',
                '-v', 'error',
                '-i', input_file,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            errors = result.stderr
            error_count = errors.count('error')
            
            # Clasificar nivel de corrupción
            if error_count == 0:
                status = "healthy"
                message = "✅ Video saludable - No se detectaron errores"
            elif error_count < 5:
                status = "minor_issues"
                message = f"⚠️ Problemas menores detectados - {error_count} errores encontrados"
            elif error_count < 20:
                status = "moderate_corruption"
                message = f"⚠️ Corrupción moderada - {error_count} errores encontrados"
            else:
                status = "severe_corruption"
                message = f"❌ Corrupción severa - {error_count} errores encontrados"
            
            return {
                'status': status,
                'error_count': error_count,
                'message': message,
                'errors': errors[:2000] if errors else ""  # Primeros 2000 caracteres
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error_count': -1,
                'message': '⏱️ Análisis excedió el tiempo límite',
                'errors': ''
            }
        except Exception as e:
            return {
                'status': 'error',
                'error_count': -1,
                'message': f'❌ Error analizando: {str(e)}',
                'errors': ''
            }
    
    @staticmethod
    def attempt_repair(input_file, output_file):
        """Intenta reparar un video corrupto"""
        try:
            cmd = [
                'ffmpeg',
                '-err_detect', 'ignore_err',
                '-i', input_file,
                '-c', 'copy',
                '-progress', 'pipe:2',
                output_file,
                '-y'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            return process
            
        except Exception as e:
            print(f"Error intentando reparar: {e}")
            return None
    
    @staticmethod
    def get_corruption_report(analysis_result):
        """Genera un reporte legible de la corrupción"""
        if not analysis_result:
            return "No hay datos de análisis"
        
        report = f"{'='*50}\n"
        report += "REPORTE DE ANÁLISIS DE CORRUPCIÓN\n"
        report += f"{'='*50}\n\n"
        
        report += f"Estado: {analysis_result['message']}\n"
        report += f"Errores detectados: {analysis_result['error_count']}\n\n"
        
        if analysis_result['status'] == 'healthy':
            report += "El video está en buen estado y no requiere reparación.\n"
        elif analysis_result['status'] in ['minor_issues', 'moderate_corruption']:
            report += "El video tiene algunos problemas pero puede ser reparable.\n"
            report += "Recomendación: Intentar reparación automática.\n"
        elif analysis_result['status'] == 'severe_corruption':
            report += "El video tiene corrupción severa.\n"
            report += "Recomendación: La reparación puede no ser exitosa.\n"
        
        if analysis_result['errors']:
            report += f"\nPrimeros errores detectados:\n{'-'*50}\n"
            report += analysis_result['errors'][:500]  # Primeros 500 caracteres
            if len(analysis_result['errors']) > 500:
                report += "\n... (más errores no mostrados)"
        
        return report