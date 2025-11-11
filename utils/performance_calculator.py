"""
Calculadora de rendimiento de juegos
Determina si un sistema puede correr un juego y a qué calidad
"""

class PerformanceCalculator:
    """Calcula el rendimiento esperado para juegos"""
    
    @staticmethod
    def calculate_game_performance(cpu, gpu, ram, requirements):
        """
        Calcular rendimiento esperado para un juego
        
        Args:
            cpu: Hardware CPU
            gpu: Hardware GPU
            ram: Hardware RAM
            requirements: GameRequirements del juego
        
        Returns:
            dict con información de rendimiento
        """
        cpu_score = cpu.benchmark_score or 0
        gpu_score = gpu.benchmark_score or 0
        ram_gb = PerformanceCalculator._get_ram_gb(ram)
        
        # Verificar requisitos mínimos
        can_run_min = (
            cpu_score >= requirements.min_cpu_score and
            gpu_score >= requirements.min_gpu_score and
            ram_gb >= requirements.min_ram_gb
        )
        
        if not can_run_min:
            return {
                'can_run': False,
                'quality': 'none',
                'fps_estimate': 0,
                'bottleneck': PerformanceCalculator._find_limiting_component(
                    cpu_score, gpu_score, ram_gb, requirements, 'minimum'
                ),
                'reason': PerformanceCalculator._get_failure_reason(
                    cpu_score, gpu_score, ram_gb, requirements
                )
            }
        
        # Determinar nivel de calidad alcanzable
        quality, fps = PerformanceCalculator._determine_quality_level(
            cpu_score, gpu_score, ram_gb, requirements
        )
        
        return {
            'can_run': True,
            'quality': quality,
            'fps_estimate': fps,
            'bottleneck': PerformanceCalculator._find_limiting_component(
                cpu_score, gpu_score, ram_gb, requirements, quality
            ),
            'reason': ''
        }
    
    @staticmethod
    def _determine_quality_level(cpu_score, gpu_score, ram_gb, req):
        """Determinar nivel de calidad y FPS estimado"""
        
        # Verificar Ultra
        if (cpu_score >= req.ultra_cpu_score and
            gpu_score >= req.ultra_gpu_score and
            ram_gb >= req.ultra_ram_gb):
            fps = PerformanceCalculator._estimate_fps(
                cpu_score, gpu_score, 
                req.ultra_cpu_score, req.ultra_gpu_score,
                base_fps=90
            )
            return 'ultra', fps
        
        # Verificar High/Recomendado
        if (cpu_score >= req.rec_cpu_score and
            gpu_score >= req.rec_gpu_score and
            ram_gb >= req.rec_ram_gb):
            fps = PerformanceCalculator._estimate_fps(
                cpu_score, gpu_score,
                req.rec_cpu_score, req.rec_gpu_score,
                base_fps=60
            )
            return 'high', fps
        
        # Verificar Medium
        if (cpu_score >= req.min_cpu_score * 1.2 and
            gpu_score >= req.min_gpu_score * 1.2):
            fps = PerformanceCalculator._estimate_fps(
                cpu_score, gpu_score,
                req.min_cpu_score * 1.2, req.min_gpu_score * 1.2,
                base_fps=45
            )
            return 'medium', fps
        
        # Mínimo (Low)
        fps = PerformanceCalculator._estimate_fps(
            cpu_score, gpu_score,
            req.min_cpu_score, req.min_gpu_score,
            base_fps=30
        )
        return 'low', fps
    
    @staticmethod
    def _estimate_fps(cpu_score, gpu_score, req_cpu, req_gpu, base_fps=60):
        """Estimar FPS basado en scores"""
        if req_cpu == 0 or req_gpu == 0:
            return base_fps
        
        cpu_ratio = cpu_score / req_cpu
        gpu_ratio = gpu_score / req_gpu
        
        # El componente más débil determina el rendimiento
        limiting_ratio = min(cpu_ratio, gpu_ratio)
        
        # Calcular FPS estimado
        estimated_fps = int(base_fps * limiting_ratio)
        
        # Limitar entre 15 y 240 FPS
        return max(15, min(240, estimated_fps))
    
    @staticmethod
    def _find_limiting_component(cpu_score, gpu_score, ram_gb, req, level):
        """Determinar qué componente está limitando"""
        if level == 'minimum':
            req_cpu = req.min_cpu_score
            req_gpu = req.min_gpu_score
            req_ram = req.min_ram_gb
        elif level == 'ultra':
            req_cpu = req.ultra_cpu_score
            req_gpu = req.ultra_gpu_score
            req_ram = req.ultra_ram_gb
        else:  
            req_cpu = req.rec_cpu_score
            req_gpu = req.rec_gpu_score
            req_ram = req.rec_ram_gb

        if req_cpu == 0 or req_gpu == 0:
            return None
        
        cpu_ratio = cpu_score / req_cpu if req_cpu > 0 else 999
        gpu_ratio = gpu_score / req_gpu if req_gpu > 0 else 999
        
        # RAM insuficiente
        if ram_gb < req_ram:
            return 'ram'
        
        # CPU limitante
        if cpu_ratio < gpu_ratio * 0.7:
            return 'cpu'
        
        # GPU limitante
        if gpu_ratio < cpu_ratio * 0.7:
            return 'gpu'
        
        return None  # Balanceado
    
    @staticmethod
    def _get_failure_reason(cpu_score, gpu_score, ram_gb, req):
        """Obtener razón de por qué no puede correr"""
        reasons = []
        
        if cpu_score < req.min_cpu_score:
            deficit = ((req.min_cpu_score - cpu_score) / req.min_cpu_score) * 100
            reasons.append(f'CPU insuficiente ({deficit:.0f}% por debajo del mínimo)')
        
        if gpu_score < req.min_gpu_score:
            deficit = ((req.min_gpu_score - gpu_score) / req.min_gpu_score) * 100
            reasons.append(f'GPU insuficiente ({deficit:.0f}% por debajo del mínimo)')
        
        if ram_gb < req.min_ram_gb:
            reasons.append(f'RAM insuficiente (requiere {req.min_ram_gb}GB, tienes {ram_gb}GB)')
        
        return ' | '.join(reasons) if reasons else 'No cumple requisitos mínimos'
    
    @staticmethod
    def _get_ram_gb(ram):
        """Obtener RAM en GB"""
        if hasattr(ram, 'get_ram_capacity_gb'):
            return ram.get_ram_capacity_gb()
        return 8  # Default
