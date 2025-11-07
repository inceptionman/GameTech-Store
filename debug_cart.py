"""
Script de diagnóstico para el carrito
"""
from app import app, db
from models.database_models import CartItem, User
from flask_login import login_user

with app.app_context():
    print("="*60)
    print("DIAGNÓSTICO DEL CARRITO")
    print("="*60)
    
    # Ver todos los items del carrito
    all_items = CartItem.query.all()
    print(f"\n📦 Total de items en cart_items: {len(all_items)}")
    
    if all_items:
        print("\n🔍 Items encontrados:")
        for item in all_items:
            print(f"  - ID: {item.id}, User ID: {item.user_id}, Type: {item.product_type}, Product ID: {item.product_id}, Qty: {item.quantity}")
    else:
        print("  ⚠️  No hay items en la tabla cart_items")
    
    # Ver usuarios
    users = User.query.all()
    print(f"\n👥 Total de usuarios: {len(users)}")
    
    if users:
        print("\n🔍 Usuarios encontrados:")
        for user in users:
            print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
            # Ver items de este usuario
            user_items = CartItem.query.filter_by(user_id=user.id).all()
            print(f"    Items en carrito: {len(user_items)}")
    
    print("\n" + "="*60)
