"""
Script de prueba para agregar productos al carrito
"""
from app import app, db
from models.database_models import CartItem, User, Game, Hardware

with app.app_context():
    print("="*60)
    print("PRUEBA DE AGREGAR AL CARRITO")
    print("="*60)
    
    # Obtener un usuario de prueba
    user = User.query.first()
    if not user:
        print("❌ No hay usuarios en la base de datos")
        exit(1)
    
    print(f"\n👤 Usuario: {user.username} (ID: {user.id})")
    
    # Obtener un juego de prueba
    game = Game.query.first()
    if not game:
        print("❌ No hay juegos en la base de datos")
        exit(1)
    
    print(f"🎮 Juego: {game.nombre} (ID: {game.id}, Stock: {game.stock})")
    
    # Intentar agregar al carrito
    try:
        new_item = CartItem(
            user_id=user.id,
            product_type='game',
            product_id=game.id,
            quantity=1
        )
        db.session.add(new_item)
        db.session.commit()
        print("\n✅ Producto agregado exitosamente al carrito!")
        
        # Verificar
        items = CartItem.query.filter_by(user_id=user.id).all()
        print(f"📦 Items en carrito del usuario: {len(items)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al agregar: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
