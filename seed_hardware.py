"""
Script para poblar la base de datos con hardware de prueba
"""
from app import app, db
from models.database_models import Hardware
import json

def seed_hardware():
    """Agregar hardware de prueba a la base de datos"""
    
    with app.app_context():
        # Verificar si ya hay hardware
        existing = Hardware.query.count()
        if existing > 0:
            print(f"✅ Ya hay {existing} componentes en la base de datos")
            return
        
        print("📦 Agregando hardware de prueba...")
        
        hardware_data = [
            # CPUs
            {
                'tipo': 'CPU',
                'marca': 'Intel',
                'modelo': 'Core i5-12400F',
                'precio': 199.99,
                'descripcion': 'Procesador de 12ª generación para gaming',
                'imagen': '/static/images/hardware/cpu-intel-i5.jpg',
                'stock': 15,
                'especificaciones': json.dumps({
                    'nucleos': 6,
                    'hilos': 12,
                    'frecuencia_base': '2.5 GHz',
                    'frecuencia_turbo': '4.4 GHz',
                    'socket': 'LGA1700',
                    'tdp': '65W'
                })
            },
            {
                'tipo': 'CPU',
                'marca': 'AMD',
                'modelo': 'Ryzen 5 5600X',
                'precio': 229.99,
                'descripcion': 'Procesador AMD de alto rendimiento',
                'imagen': '/static/images/hardware/cpu-amd-5600x.jpg',
                'stock': 12,
                'especificaciones': json.dumps({
                    'nucleos': 6,
                    'hilos': 12,
                    'frecuencia_base': '3.7 GHz',
                    'frecuencia_turbo': '4.6 GHz',
                    'socket': 'AM4',
                    'tdp': '65W'
                })
            },
            # GPUs
            {
                'tipo': 'GPU',
                'marca': 'NVIDIA',
                'modelo': 'RTX 4060 Ti',
                'precio': 449.99,
                'descripcion': 'Tarjeta gráfica de última generación',
                'imagen': '/static/images/hardware/gpu-rtx-4060ti.jpg',
                'stock': 8,
                'especificaciones': json.dumps({
                    'memoria': '8 GB GDDR6',
                    'velocidad_memoria': '18 Gbps',
                    'cuda_cores': 4352,
                    'boost_clock': '2.54 GHz',
                    'tdp': '160W',
                    'conectores': '1x 8-pin'
                })
            },
            {
                'tipo': 'GPU',
                'marca': 'AMD',
                'modelo': 'RX 7600',
                'precio': 299.99,
                'descripcion': 'GPU AMD para gaming 1080p',
                'imagen': '/static/images/hardware/gpu-rx-7600.jpg',
                'stock': 10,
                'especificaciones': json.dumps({
                    'memoria': '8 GB GDDR6',
                    'velocidad_memoria': '16 Gbps',
                    'stream_processors': 2048,
                    'boost_clock': '2.65 GHz',
                    'tdp': '165W',
                    'conectores': '1x 8-pin'
                })
            },
            # RAM
            {
                'tipo': 'RAM',
                'marca': 'Corsair',
                'modelo': 'Vengeance RGB 16GB',
                'precio': 79.99,
                'descripcion': 'Memoria DDR4 de alto rendimiento con RGB',
                'imagen': '/static/images/hardware/ram-corsair-16gb.jpg',
                'stock': 25,
                'especificaciones': json.dumps({
                    'capacidad': '16 GB',
                    'tipo': 'DDR4',
                    'frecuencia': '3200 MHz',
                    'latencia': 'CL16',
                    'modulos': '2x8GB',
                    'rgb': 'Sí'
                })
            },
            {
                'tipo': 'RAM',
                'marca': 'G.Skill',
                'modelo': 'Trident Z5 32GB',
                'precio': 149.99,
                'descripcion': 'Memoria DDR5 de última generación',
                'imagen': '/static/images/hardware/ram-gskill-32gb.jpg',
                'stock': 18,
                'especificaciones': json.dumps({
                    'capacidad': '32 GB',
                    'tipo': 'DDR5',
                    'frecuencia': '6000 MHz',
                    'latencia': 'CL36',
                    'modulos': '2x16GB',
                    'rgb': 'Sí'
                })
            },
            # Motherboards
            {
                'tipo': 'Motherboard',
                'marca': 'ASUS',
                'modelo': 'ROG STRIX B660-A',
                'precio': 189.99,
                'descripcion': 'Placa base gaming para Intel 12ª gen',
                'imagen': '/static/images/hardware/mb-asus-b660.jpg',
                'stock': 10,
                'especificaciones': json.dumps({
                    'socket': 'LGA1700',
                    'chipset': 'B660',
                    'formato': 'ATX',
                    'memoria': 'DDR4',
                    'slots_ram': 4,
                    'max_ram': '128 GB',
                    'pcie': 'PCIe 4.0',
                    'rgb': 'Aura Sync'
                })
            },
            {
                'tipo': 'Motherboard',
                'marca': 'MSI',
                'modelo': 'B550 TOMAHAWK',
                'precio': 169.99,
                'descripcion': 'Placa base AMD con PCIe 4.0',
                'imagen': '/static/images/hardware/mb-msi-b550.jpg',
                'stock': 12,
                'especificaciones': json.dumps({
                    'socket': 'AM4',
                    'chipset': 'B550',
                    'formato': 'ATX',
                    'memoria': 'DDR4',
                    'slots_ram': 4,
                    'max_ram': '128 GB',
                    'pcie': 'PCIe 4.0',
                    'rgb': 'Mystic Light'
                })
            }
        ]
        
        # Agregar cada componente
        for data in hardware_data:
            hardware = Hardware(**data)
            db.session.add(hardware)
            print(f"  ✅ Agregado: {data['marca']} {data['modelo']}")
        
        # Guardar cambios
        db.session.commit()
        print(f"\n✅ {len(hardware_data)} componentes agregados exitosamente!")
        
        # Verificar
        total = Hardware.query.count()
        print(f"📊 Total en base de datos: {total} componentes")

if __name__ == '__main__':
    seed_hardware()
