from .models import Cart

def cart_total_items(request):
    total_items = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            total_items = sum([item.quantity for item in cart.cartitem_set.all()])
    else:
        cart = request.session.get('cart', {})
        total_items = sum(item['quantity'] for item in cart.values())
    
    return {'total_items_in_cart': total_items}
