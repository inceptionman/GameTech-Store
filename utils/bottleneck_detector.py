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
        Detectar cuellos de botella.

        Args:
            cpu: Objeto Hardware de tipo CPU
            gpu: Objeto Hardware de tipo GPU
            ram: Objeto Hardware de tipo RAM

        Returns:
            dict con información del cuello de botella
        """
        result = BottleneckDetector._init_result()
        cpu_score, gpu_score = cpu.benchmark_score or 0, gpu.benchmark_score or 0
        ram_gb = BottleneckDetector._extract_ram_gb(ram)

        if cpu_score == 0 or gpu_score == 0:
            result['description'] = 'No hay datos de benchmark suficientes para analizar.'
            return result

        def apply_thresholds(ratio, thresholds, is_cpu_bottleneck):
            for threshold, severity, percent, multiplier, desc, rec in thresholds:
                if ratio >= threshold:
                    kind = 'cpu' if is_cpu_bottleneck else 'gpu'
                    BottleneckDetector._update_result(result, severity, percent, desc, rec, multiplier, cpu_score, gpu_score, kind)
                    return True
            return False

        if BottleneckDetector._is_cpu_bottleneck(gpu_score, cpu_score):
            ratio = gpu_score / cpu_score
            if apply_thresholds(ratio, BottleneckDetector._cpu_thresholds(), True):
                result['has_bottleneck'] = True
                result['type'] = 'cpu'
        elif BottleneckDetector._is_gpu_bottleneck(gpu_score, cpu_score):
            ratio = cpu_score / gpu_score
            if apply_thresholds(ratio, BottleneckDetector._gpu_thresholds(), False):
                result['has_bottleneck'] = True
                result['type'] = 'gpu'

        BottleneckDetector._check_ram_bottleneck(result, ram_gb)
        BottleneckDetector._check_balanced(result)

        return result

    # Métodos auxiliares sugeridos como métodos estáticos:
    @staticmethod
    def _init_result():
        return {
            'has_bottleneck': False, 'type': 'balanced', 'severity': 'none',
            'description': '', 'recommendations': [], 'percentage_loss': 0
        }

    @staticmethod
    def _update_result(result, severity, percent, desc, rec, multiplier, cpu_score, gpu_score, kind):
        result['severity'] = severity
        result['percentage_loss'] = percent
        result['description'] = desc
        if kind == 'cpu':
            result['recommendations'].append(rec.format(score=int(gpu_score * multiplier)))
        else:
            result['recommendations'].append(rec.format(score=int(cpu_score * multiplier)))

    @staticmethod
    def _cpu_thresholds():
        return [
            (1.5, "severe", 25, 0.4, "Tu GPU es muy superior...", "💡 Un CPU con score ~{score}+..."),
            (1.15, "moderate", 12, 0.6, "Tu GPU es ligeramente más potente...", "💡 Un CPU con score ~{score}+...")
            # ...otros thresholds según tu lógica
        ]

    @staticmethod
    def _gpu_thresholds():
        return [
            (1.15, "moderate", 13, 0.5, "Tu CPU es ligeramente más potente...", "💡 Una GPU con score ~{score}+...")
            # ...otros thresholds según tu lógica
        ]

    @staticmethod
    def _is_cpu_bottleneck(gpu_score, cpu_score):
        return gpu_score / cpu_score >= BottleneckDetector.MILD_RATIO

    @staticmethod
    def _is_gpu_bottleneck(gpu_score, cpu_score):
        return cpu_score / gpu_score >= BottleneckDetector.MILD_RATIO

    @staticmethod
    def _check_ram_bottleneck(result, ram_gb):
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

    @staticmethod
    def _check_balanced(result):
        if not result['has_bottleneck']:
            result['description'] = (
                '✅ **¡Sistema Balanceado!**\n\n'
                'Tu configuración está bien equilibrada. '
                'No hay cuellos de botella significativos.'
            )

    
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
