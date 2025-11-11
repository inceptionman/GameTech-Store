#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular la base de datos con hardware de ejemplo
"""
import json
from app import app, db
from models.database_models import Hardware

def add_hardware():
    """Agregar hardware de ejemplo"""
    with app.app_context():
        # Verificar si ya existen datos
        cpus_count = Hardware.query.filter_by(tipo='CPU').count()
        if cpus_count > 0:
            print("✓ Hardware ya existe en BD. Saltando...")
            return
        
        hardware_data = [
            # CPUs
            {
                'marca': 'Intel',
                'modelo': 'Core i5-12400',
                'tipo': 'CPU',
                'precio': 150,
                'cores': 6,
                'threads': 12,
                'tdp_watts': 65,
                'socket': 'LGA1700',
                'especificaciones': json.dumps({
                    'nucleos': 6,
                    'hilos': 12,
                    'velocidad_base': '2.5 GHz',
                    'turbo_max': '4.4 GHz',
                    'tdp': 65,
                    'socket': 'LGA1700'
                })
            },
            {
                'marca': 'AMD',
                'modelo': 'Ryzen 5 5500',
                'tipo': 'CPU',
                'precio': 140,
                'cores': 6,
                'threads': 12,
                'tdp_watts': 65,
                'socket': 'AM4',
                'especificaciones': json.dumps({
                    'nucleos': 6,
                    'hilos': 12,
                    'velocidad_base': '3.6 GHz',
                    'turbo_max': '4.2 GHz',
                    'tdp': 65,
                    'socket': 'AM4'
                })
            },
            {
                'marca': 'Intel',
                'modelo': 'Core i7-13700K',
                'tipo': 'CPU',
                'precio': 400,
                'cores': 16,
                'threads': 24,
                'tdp_watts': 125,
                'socket': 'LGA1700',
                'especificaciones': json.dumps({
                    'nucleos': 16,
                    'hilos': 24,
                    'velocidad_base': '3.4 GHz',
                    'turbo_max': '5.4 GHz',
                    'tdp': 125,
                    'socket': 'LGA1700'
                })
            },
            {
                'marca': 'AMD',
                'modelo': 'Ryzen 7 7700X',
                'tipo': 'CPU',
                'precio': 380,
                'cores': 8,
                'threads': 16,
                'tdp_watts': 105,
                'socket': 'AM5',
                'especificaciones': json.dumps({
                    'nucleos': 8,
                    'hilos': 16,
                    'velocidad_base': '4.5 GHz',
                    'turbo_max': '5.4 GHz',
                    'tdp': 105,
                    'socket': 'AM5'
                })
            },
            
            # GPUs
            {
                'marca': 'NVIDIA',
                'modelo': 'RTX 3060',
                'tipo': 'GPU',
                'precio': 280,
                'vram_gb': 12,
                'tdp_watts': 170,
                'especificaciones': json.dumps({
                    'memoria': '12 GB GDDR6',
                    'cuda_cores': 3584,
                    'velocidad_clock': '1.32 GHz',
                    'tdp': 170,
                    'conectores': 'PCIe 4.0'
                })
            },
            {
                'marca': 'AMD',
                'modelo': 'RX 6700 XT',
                'tipo': 'GPU',
                'precio': 300,
                'vram_gb': 12,
                'tdp_watts': 230,
                'especificaciones': json.dumps({
                    'memoria': '12 GB GDDR6',
                    'stream_processors': 2560,
                    'velocidad_clock': '2.5 GHz',
                    'tdp': 230,
                    'conectores': 'PCIe 4.0'
                })
            },
            {
                'marca': 'NVIDIA',
                'modelo': 'RTX 4070',
                'tipo': 'GPU',
                'precio': 600,
                'vram_gb': 12,
                'tdp_watts': 200,
                'especificaciones': json.dumps({
                    'memoria': '12 GB GDDR6X',
                    'cuda_cores': 5888,
                    'velocidad_clock': '2.48 GHz',
                    'tdp': 200,
                    'conectores': 'PCIe 4.0'
                })
            },
            {
                'marca': 'NVIDIA',
                'modelo': 'RTX 4090',
                'tipo': 'GPU',
                'precio': 1600,
                'vram_gb': 24,
                'tdp_watts': 450,
                'especificaciones': json.dumps({
                    'memoria': '24 GB GDDR6X',
                    'cuda_cores': 16384,
                    'velocidad_clock': '2.52 GHz',
                    'tdp': 450,
                    'conectores': 'PCIe 4.0'
                })
            },
            
            # RAMs
            {
                'marca': 'Corsair',
                'modelo': 'Vengeance 16GB DDR4-3200',
                'tipo': 'RAM',
                'precio': 50,
                'especificaciones': json.dumps({
                    'capacidad': '16 GB',
                    'tipo': 'DDR4',
                    'velocidad': '3200 MHz',
                    'latencia': 'CAS 16',
                    'modulos': 2
                })
            },
            {
                'marca': 'G.Skill',
                'modelo': 'Trident Z5 32GB DDR5-6000',
                'tipo': 'RAM',
                'precio': 120,
                'especificaciones': json.dumps({
                    'capacidad': '32 GB',
                    'tipo': 'DDR5',
                    'velocidad': '6000 MHz',
                    'latencia': 'CAS 30',
                    'modulos': 2
                })
            },
            {
                'marca': 'Kingston',
                'modelo': 'Fury Beast 32GB DDR4-3200',
                'tipo': 'RAM',
                'precio': 70,
                'especificaciones': json.dumps({
                    'capacidad': '32 GB',
                    'tipo': 'DDR4',
                    'velocidad': '3200 MHz',
                    'latencia': 'CAS 16',
                    'modulos': 2
                })
            },
            {
                'marca': 'Corsair',
                'modelo': 'Dominator DDR5 64GB-5600',
                'tipo': 'RAM',
                'precio': 250,
                'especificaciones': json.dumps({
                    'capacidad': '64 GB',
                    'tipo': 'DDR5',
                    'velocidad': '5600 MHz',
                    'latencia': 'CAS 28',
                    'modulos': 2
                })
            },
        ]
        
        for hw_data in hardware_data:
            hw = Hardware(
                marca=hw_data['marca'],
                modelo=hw_data['modelo'],
                tipo=hw_data['tipo'],
                precio=hw_data['precio'],
                cores=hw_data.get('cores', 0),
                threads=hw_data.get('threads', 0),
                vram_gb=hw_data.get('vram_gb', 0),
                tdp_watts=hw_data.get('tdp_watts', 0),
                socket=hw_data.get('socket', ''),
                especificaciones=hw_data['especificaciones']
            )
            db.session.add(hw)
        
        db.session.commit()
        print(f"✓ {len(hardware_data)} componentes de hardware agregados")

if __name__ == '__main__':
    add_hardware()
    print("✅ Hardware poblado exitosamente")
