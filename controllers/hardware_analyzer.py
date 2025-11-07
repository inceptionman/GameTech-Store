"""
Controlador para el analizador de hardware
Permite a los usuarios analizar su configuración y ver compatibilidad con juegos
"""
from flask import Blueprint, render_template, request, jsonify
from models.database_models import Hardware, Game, GameRequirements
from utils.bottleneck_detector import BottleneckDetector
from utils.performance_calculator import PerformanceCalculator

analyzer_bp = Blueprint('analyzer', __name__)

@analyzer_bp.route('/analizador-hardware')
def hardware_analyzer_page():
    """Página principal del analizador de hardware"""
    # Cargar componentes para los selectores
    cpus = Hardware.get_hardware_by_tipo('CPU')
    gpus = Hardware.get_hardware_by_tipo('GPU')
    rams = Hardware.get_hardware_by_tipo('RAM')
    
    return render_template('hardware_checker.html',
                         cpus=cpus,
                         gpus=gpus,
                         rams=rams)

@analyzer_bp.route('/api/analizar-hardware', methods=['POST'])
def analyze_hardware():
    """API para analizar la configuración del usuario"""
    try:
        data = request.get_json()
        
        cpu_id = data.get('cpu_id')
        gpu_id = data.get('gpu_id')
        ram_id = data.get('ram_id')
        
        # Validar datos
        if not all([cpu_id, gpu_id, ram_id]):
            return jsonify({'error': 'Faltan componentes'}), 400
        
        # Obtener componentes
        cpu = Hardware.get_hardware_by_id(cpu_id)
        gpu = Hardware.get_hardware_by_id(gpu_id)
        ram = Hardware.get_hardware_by_id(ram_id)
        
        if not all([cpu, gpu, ram]):
            return jsonify({'error': 'Componentes no encontrados'}), 404
        
        # 1. Calcular puntuación del sistema
        system_score = calculate_system_score(cpu, gpu, ram)
        
        # 2. Detectar cuellos de botella
        bottlenecks = BottleneckDetector.detect(cpu, gpu, ram)
        
        # 3. Analizar compatibilidad con juegos
        games_analysis = analyze_game_compatibility(cpu, gpu, ram)
        
        # 4. Generar recomendaciones
        recommendations = generate_recommendations(bottlenecks, system_score)
        
        return jsonify({
            'success': True,
            'system_score': system_score,
            'bottlenecks': bottlenecks,
            'games': games_analysis,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_system_score(cpu, gpu, ram):
    """Calcular puntuación general del sistema"""
    cpu_score = cpu.benchmark_score or 0
    gpu_score = gpu.benchmark_score or 0
    ram_gb = ram.get_ram_capacity_gb() if hasattr(ram, 'get_ram_capacity_gb') else 8
    ram_score = ram_gb * 100  # 16GB = 1600 puntos
    
    # Ponderación: GPU 50%, CPU 35%, RAM 15%
    total = (gpu_score * 0.5) + (cpu_score * 0.35) + (ram_score * 0.15)
    
    return {
        'total': int(total),
        'cpu_score': cpu_score,
        'gpu_score': gpu_score,
        'ram_score': ram_score,
        'ram_gb': ram_gb,
        'tier': get_performance_tier(total),
        'components': {
            'cpu': f'{cpu.marca} {cpu.modelo}',
            'gpu': f'{gpu.marca} {gpu.modelo}',
            'ram': f'{ram_gb}GB RAM'
        }
    }

def get_performance_tier(score):
    """Determinar el nivel de rendimiento"""
    if score >= 15000:
        return 'Ultra High-End (4K Ultra)'
    elif score >= 10000:
        return 'High-End (1440p Ultra)'
    elif score >= 7000:
        return 'Mid-High (1080p Ultra)'
    elif score >= 4000:
        return 'Mid-Range (1080p Medium-High)'
    else:
        return 'Entry Level (1080p Low-Medium)'

def analyze_game_compatibility(cpu, gpu, ram):
    """Analizar qué juegos puede correr el usuario"""
    games = Game.get_all_games()
    
    results = {
        'can_run_ultra': [],
        'can_run_high': [],
        'can_run_medium': [],
        'can_run_low': [],
        'cannot_run': []
    }
    
    for game in games:
        requirements = GameRequirements.get_by_game_id(game.id)
        
        if not requirements:
            continue  # Skip juegos sin requisitos
        
        # Calcular rendimiento
        performance = PerformanceCalculator.calculate_game_performance(
            cpu, gpu, ram, requirements
        )
        
        game_data = {
            'id': game.id,
            'nombre': game.nombre,
            'imagen': game.imagen,
            'precio': game.precio,
            'expected_fps': performance['fps_estimate'],
            'quality': performance['quality'],
            'bottleneck': performance['bottleneck'],
            'reason': performance.get('reason', '')
        }
        
        # Clasificar por calidad
        if not performance['can_run']:
            results['cannot_run'].append(game_data)
        elif performance['quality'] == 'ultra':
            results['can_run_ultra'].append(game_data)
        elif performance['quality'] == 'high':
            results['can_run_high'].append(game_data)
        elif performance['quality'] == 'medium':
            results['can_run_medium'].append(game_data)
        else:  # low
            results['can_run_low'].append(game_data)
    
    return results

def generate_recommendations(bottlenecks, system_score):
    """Generar recomendaciones de mejora"""
    recommendations = []
    
    # Recomendaciones de bottleneck
    if bottlenecks['has_bottleneck']:
        recommendations.extend(bottlenecks['recommendations'])
    
    # Recomendaciones por tier
    total_score = system_score['total']
    
    if total_score < 7000:
        recommendations.append(
            '💡 Tu sistema es entry-level. Considera actualizar GPU y CPU para mejor experiencia.'
        )
    elif total_score < 10000:
        recommendations.append(
            '💡 Tu sistema es mid-range. Una GPU mejor te daría un salto significativo en rendimiento.'
        )
    
    # Recomendación de RAM
    if system_score['ram_gb'] < 16:
        recommendations.append(
            '💾 16GB de RAM es el estándar actual para gaming. Considera expandir.'
        )
    
    return recommendations
