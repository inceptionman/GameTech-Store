"""
Detector de cuellos de botella en configuraciones de hardware
Analiza el balance entre CPU, GPU y RAM
"""
import re

class BottleneckDetector:
    """Detecta y analiza cuellos de botella en hardware"""
    
    # Umbrales de desequilibrio
    SEVERE_RATIO = 3.0   # 3x diferencia = severo
    MODERATE_RATIO = 2.0 # 2x diferencia = moderado
    MILD_RATIO = 1.5     # 1.5x diferencia = leve
    
    @staticmethod
    def detect(cpu, gpu, ram):
        """
        Detectar cuellos de botella
        
        Args:
            cpu: Objeto Hardware de tipo CPU
            gpu: Objeto Hardware de tipo GPU
            ram: Objeto Hardware de tipo RAM
        
        Returns:
            dict con información del cuello de botella
        """
        result = {
            'has_bottleneck': False,
            'type': 'balanced',
            'severity': 'none',
            'description': '',
            'recommendations': [],
            'percentage_loss': 0
        }
        
        cpu_score = cpu.benchmark_score or 0
        gpu_score = gpu.benchmark_score or 0
        ram_gb = BottleneckDetector._extract_ram_gb(ram)
        
        # Validar datos
        if cpu_score == 0 or gpu_score == 0:
            result['description'] = 'No hay datos de benchmark suficientes para analizar.'
            return result
        
        # Analizar balance CPU/GPU
        gpu_cpu_ratio = gpu_score / cpu_score
        
        # CPU BOTTLENECK (GPU más potente que CPU)
        if gpu_cpu_ratio >= BottleneckDetector.MILD_RATIO:
            result['has_bottleneck'] = True
            result['type'] = 'cpu'
            
            if gpu_cpu_ratio >= BottleneckDetector.SEVERE_RATIO:
                result['severity'] = 'severe'
                result['percentage_loss'] = 40
                result['description'] = (
                    f'⚠️ **Cuello de botella SEVERO en CPU**\n\n'
                    f'Tu GPU ({gpu.marca} {gpu.modelo}) es {gpu_cpu_ratio:.1f}x más potente '
                    f'que tu CPU ({cpu.marca} {cpu.modelo}).\n\n'
                    f'**Impacto:** Pérdida de 30-50% del rendimiento de la GPU.'
                )
                result['recommendations'].append(
                    f'🔧 **URGENTE:** Actualizar CPU a score ~{int(gpu_score * 0.6)}+ para aprovechar la GPU.'
                )
            
            elif gpu_cpu_ratio >= BottleneckDetector.MODERATE_RATIO:
                result['severity'] = 'moderate'
                result['percentage_loss'] = 25
                result['description'] = (
                    f'⚠️ **Cuello de botella MODERADO en CPU**\n\n'
                    f'Tu GPU es {gpu_cpu_ratio:.1f}x más potente que tu CPU. '
                    f'En juegos exigentes notarás limitaciones.\n\n'
                    f'**Impacto:** Pérdida de 15-30% del rendimiento.'
                )
                result['recommendations'].append(
                    f'🔧 Considera actualizar CPU a score ~{int(gpu_score * 0.7)}+'
                )
            
            else:  # MILD
                result['severity'] = 'mild'
                result['percentage_loss'] = 10
                result['description'] = (
                    f'ℹ️ **Cuello de botella LEVE en CPU**\n\n'
                    f'Tu GPU es ligeramente más potente (ratio {gpu_cpu_ratio:.1f}x). '
                    f'Funcionará bien en la mayoría de juegos.\n\n'
                    f'**Impacto:** Pérdida de 5-15% en algunos juegos.'
                )
                result['recommendations'].append(
                    f'💡 Un CPU con score ~{int(gpu_score * 0.8)}+ optimizaría tu sistema.'
                )
        
        # GPU BOTTLENECK (CPU más potente que GPU)
        elif gpu_cpu_ratio < (1 / BottleneckDetector.MILD_RATIO):
            cpu_gpu_ratio = cpu_score / gpu_score
            result['has_bottleneck'] = True
            result['type'] = 'gpu'
            
            if cpu_gpu_ratio >= BottleneckDetector.SEVERE_RATIO:
                result['severity'] = 'severe'
                result['percentage_loss'] = 40
                result['description'] = (
                    f'⚠️ **Cuello de botella SEVERO en GPU**\n\n'
                    f'Tu CPU es {cpu_gpu_ratio:.1f}x más potente que tu GPU. '
                    f'La GPU está limitando el rendimiento gráfico.\n\n'
                    f'**Impacto:** Limitación severa en FPS y calidad gráfica.'
                )
                result['recommendations'].append(
                    f'🔧 **URGENTE:** Actualizar GPU a score ~{int(cpu_score * 0.6)}+'
                )
            
            elif cpu_gpu_ratio >= BottleneckDetector.MODERATE_RATIO:
                result['severity'] = 'moderate'
                result['percentage_loss'] = 25
                result['description'] = (
                    f'⚠️ **Cuello de botella MODERADO en GPU**\n\n'
                    f'Tu CPU es {cpu_gpu_ratio:.1f}x más potente que tu GPU. '
                    f'Podrías mejorar significativamente con una GPU mejor.\n\n'
                    f'**Impacto:** FPS limitados en juegos modernos.'
                )
                result['recommendations'].append(
                    f'🔧 Considera actualizar GPU a score ~{int(cpu_score * 0.7)}+'
                )
            
            else:  # MILD
                result['severity'] = 'mild'
                result['percentage_loss'] = 10
                result['description'] = (
                    f'ℹ️ **Cuello de botella LEVE en GPU**\n\n'
                    f'Tu CPU es ligeramente más potente. '
                    f'Una GPU mejor aprovecharía más tu CPU.\n\n'
                    f'**Impacto:** Limitación menor en FPS.'
                )
                result['recommendations'].append(
                    f'💡 Una GPU con score ~{int(cpu_score * 0.8)}+ mejoraría el rendimiento.'
                )
        
        # Verificar RAM insuficiente
        if ram_gb < 16:
            result['has_bottleneck'] = True
            if result['type'] == 'balanced':
                result['type'] = 'ram'
            result['severity'] = 'moderate' if ram_gb < 8 else 'mild'
            result['description'] += (
                f'\n\n⚠️ **RAM Insuficiente**\n'
                f'Solo tienes {ram_gb}GB de RAM. Los juegos modernos recomiendan 16GB.\n'
                f'**Impacto:** Posibles stutters y limitaciones en juegos exigentes.'
            )
            result['recommendations'].append(
                f'💾 Actualizar a 16GB o 32GB de RAM para mejor rendimiento.'
            )
        
        # Sistema balanceado
        if not result['has_bottleneck']:
            result['description'] = (
                '✅ **¡Sistema Balanceado!**\n\n'
                'Tu configuración está bien equilibrada. '
                'No hay cuellos de botella significativos.'
            )
        
        return result
    
    @staticmethod
    def _extract_ram_gb(ram):
        """Extraer capacidad de RAM en GB"""
        if hasattr(ram, 'get_ram_capacity_gb'):
            return ram.get_ram_capacity_gb()
        
        # Fallback: extraer de especificaciones
        specs = ram.get_especificaciones() if hasattr(ram, 'get_especificaciones') else {}
        capacity_str = specs.get('capacidad', '8 GB')
        
        match = re.search(r'(\d+)\s*GB', str(capacity_str), re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 8  # Default
