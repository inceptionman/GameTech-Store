"""
Script para agregar CSRF tokens a todos los formularios HTML
"""
import os
import re

def add_csrf_to_file(filepath):
    """Agregar CSRF token a formularios en un archivo HTML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar formularios POST sin CSRF token
    pattern = r'(<form[^>]*method=["\']POST["\'][^>]*>)(\s*)(?!.*?csrf_token)'
    
    # Reemplazo: agregar input hidden con csrf_token
    replacement = r'\1\2<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">\2'
    
    # Verificar si ya tiene csrf_token
    if 'csrf_token()' in content:
        return False, "Ya tiene CSRF token"
    
    # Buscar formularios POST
    if not re.search(pattern, content, re.DOTALL):
        return False, "No hay formularios POST"
    
    # Aplicar reemplazo
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Guardar archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "CSRF token agregado"

def process_templates():
    """Procesar todos los templates"""
    templates_dir = 'templates'
    modified_files = []
    skipped_files = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                success, message = add_csrf_to_file(filepath)
                
                if success:
                    modified_files.append(filepath)
                    print(f"✅ {filepath}: {message}")
                else:
                    skipped_files.append((filepath, message))
                    print(f"⏭️  {filepath}: {message}")
    
    print("\n" + "="*60)
    print(f"Archivos modificados: {len(modified_files)}")
    print(f"Archivos omitidos: {len(skipped_files)}")
    print("="*60)
    
    if modified_files:
        print("\nArchivos modificados:")
        for f in modified_files:
            print(f"  - {f}")

if __name__ == '__main__':
    print("Agregando CSRF tokens a formularios...")
    print("="*60)
    process_templates()
