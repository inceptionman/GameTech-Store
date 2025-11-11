#!/usr/bin/env python
"""
Script de prueba rápido para el analizador de hardware
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db

def test_analyzer():
    """Prueba el analizador de hardware"""
    with app.app_context():
        from models.database_models import Hardware
        
        print("📊 Probando Analizador de Hardware\n")
        
        # Obtener hardware disponible
        cpus = Hardware.get_hardware_by_tipo('CPU')
        gpus = Hardware.get_hardware_by_tipo('GPU')
        rams = Hardware.get_hardware_by_tipo('RAM')
        
        print(f"✓ CPUs disponibles: {len(cpus)}")
        print(f"✓ GPUs disponibles: {len(gpus)}")
        print(f"✓ RAMs disponibles: {len(rams)}")
        
        if not (cpus and gpus and rams):
            print("\n⚠️  No hay hardware disponible. Agrega algunos primero.")
            return False
        
        # Seleccionar el primero de cada uno
        cpu = cpus[0]
        gpu = gpus[0]
        ram = rams[0]
        
        print(f"\n🔧 Hardware seleccionado:")
        print(f"   CPU: {cpu.marca} {cpu.modelo}")
        print(f"   GPU: {gpu.marca} {gpu.modelo}")
        print(f"   RAM: {ram.marca} {ram.modelo}")
        
        # Probar la API
        print("\n🧪 Probando API /api/analizar-hardware...")
        
        from controllers.hardware_analyzer import (
            calculate_system_score, 
            analyze_game_compatibility,
            generate_recommendations
        )
        from utils.bottleneck_detector import BottleneckDetector
        
        try:
            # Calcular puntuación
            system_score = calculate_system_score(cpu, gpu, ram)
            print(f"✓ Puntuación del sistema: {system_score['total']}")
            print(f"  Tier: {system_score['tier']}")
            
            # Detectar cuellos de botella
            bottlenecks = BottleneckDetector.detect(cpu, gpu, ram)
            print(f"✓ Análisis de cuello de botella: {bottlenecks.get('type', 'balanced')}")
            
            # Analizar compatibilidad con juegos
            games = analyze_game_compatibility(cpu, gpu, ram)
            total_games = sum(len(v) for v in games.values())
            print(f"✓ Juegos analizados: {total_games}")
            
            # Generar recomendaciones
            recommendations = generate_recommendations(bottlenecks, system_score)
            print(f"✓ Recomendaciones generadas: {len(recommendations)}")
            
            print("\n✅ ¡Todo funciona correctamente!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_analyzer()
    sys.exit(0 if success else 1)
