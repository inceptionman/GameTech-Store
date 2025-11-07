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
        
        if cpu_score == 0 or gpu_score == 0:
            result['description'] = 'No hay datos de benchmark suficientes para analizar.'
            return result

        def handle_cpu_bottleneck(ratio):
            result['has_bottleneck'] = True
            result['type'] = 'cpu'
            thresholds = [
                (BottleneckDetector.SEVERE_RATIO, 'severe', 40, 0.6,
                '⚠️ **Cuello de botella SEVERO en CPU**\n\n'
                f'Tu GPU ({gpu.marca} {gpu.modelo}) es {ratio:.1f}x más potente '
                f'que tu CPU ({cpu.marca} {cpu.modelo}).\n\n'
                '**Impacto:** Pérdida de 30-50% del rendimiento de la GPU.',
                '🔧 **URGENTE:** Actualizar CPU a score ~{score}+ para aprovechar la GPU.'),
                (BottleneckDetector.MODERATE_RATIO, 'moderate', 25, 0.7,
                '⚠️ **Cuello de botella MODERADO en CPU**\n\n'
                f'Tu GPU es {ratio:.1f}x más potente que tu CPU. '
                'En juegos exigentes notarás limitaciones.\n\n'
                '**Impacto:** Pérdida de 15-30% del rendimiento.',
                '🔧 Considera actualizar CPU a score ~{score}+'),
                (0, 'mild', 10, 0.8,  # covers all lower ratios
                'ℹ️ **Cuello de botella LEVE en CPU**\n\n'
                f'Tu GPU es ligeramente más potente (ratio {ratio:.1f}x). '
                'Funcionará bien en la mayoría de juegos.\n\n'
                '**Impacto:** Pérdida de 5-15% en algunos juegos.',
                '💡 Un CPU con score ~{score}+ optimizaría tu sistema.')
            ]
            for threshold, severity, percent, multiplier, desc, rec in thresholds:
                if ratio >= threshold:
                    result['severity'] = severity
                    result['percentage_loss'] = percent
                    result['description'] = desc
                    result['recommendations'].append(
                        rec.format(score=int(gpu_score * multiplier))
                    )
                    break

        def handle_gpu_bottleneck(ratio):
            cpu_gpu_ratio = cpu_score / gpu_score
            result['has_bottleneck'] = True
            result['type'] = 'gpu'
            thresholds = [
                (BottleneckDetector.SEVERE_RATIO, 'severe', 40, 0.6,
                '⚠️ **Cuello de botella SEVERO en GPU**\n\n'
                f'Tu CPU es {cpu_gpu_ratio:.1f}x más potente que tu GPU. '
                'La GPU está limitando el rendimiento gráfico.\n\n'
                '**Impacto:** Limitación severa en FPS y calidad gráfica.',
                '🔧 **URGENTE:** Actualizar GPU a score ~{score}+'),
                (BottleneckDetector.MODERATE_RATIO, 'moderate', 25, 0.7,
                '⚠️ **Cuello de botella MODERADO en GPU**\n\n'
                f'Tu CPU es {cpu_gpu_ratio:.1f}x más potente que tu GPU. '
                'Podrías mejorar significativamente con una GPU mejor.\n\n'
                '**Impacto:** FPS limitados en juegos modernos.',
                '🔧 Considera actualizar GPU a score ~{score}+'),
                (0, 'mild', 10, 0.8,
                'ℹ️ **Cuello de botella LEVE en GPU**\n\n'
                'Tu CPU es ligeramente más potente. '
                'Una GPU mejor aprovecharía más tu CPU.\n\n'
                '**Impacto:** Limitación menor en FPS.',
                '💡 Una GPU con score ~{score}+ mejoraría el rendimiento.')
            ]
            for threshold, severity, percent, multiplier, desc, rec in thresholds:
                if cpu_gpu_ratio >= threshold:
                    result['severity'] = severity
                    result['percentage_loss'] = percent
                    result['description'] = desc
                    result['recommendations'].append(
                        rec.format(score=int(cpu_score * multiplier))
                    )
                    break

        gpu_cpu_ratio = gpu_score / cpu_score
        if gpu_cpu_ratio >= BottleneckDetector.MILD_RATIO:
            handle_cpu_bottleneck(gpu_cpu_ratio)
        elif gpu_cpu_ratio < (1 / BottleneckDetector.MILD_RATIO):
            handle_gpu_bottleneck(gpu_cpu_ratio)
        
        # Verificar RAM insuficiente
        if ram_gb < 16:
            result['has_bottleneck'] = True
            if result['type'] == 'balanced':
                result['type'] = 'ram'
            result['severity'] = 'moderate' if ram_gb < 8 else 'mild'
            result['description'] += (
                f'\n\n⚠️ **RAM Insuficiente**\n'
                f'Solo tienes {ram_gb}GB de RAM. Los juegos modernos recomiendan 16GB.\n'
                '**Impacto:** Posibles stutters y limitaciones en juegos exigentes.'
            )
            result['recommendations'].append(
                '💾 Actualizar a 16GB o 32GB de RAM para mejor rendimiento.'
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
