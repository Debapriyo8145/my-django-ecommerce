from .models import Cart
from .models import Wishlist

def cart_context(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.Item.price * item.quantity for item in cart_items)
    else:
        cart_count = 0
        cart_items = []
        total_price = 0
    
    return {
        'cart_count': cart_count,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    


def wishlist_context(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.select_related('item').filter(user=request.user)
        wishlist_count = wishlist_items.count()
        wishlist_total = sum(item.item.price for item in wishlist_items if item.item)
    else:
        wishlist_items = []
        wishlist_count = 0
        wishlist_total = 0

    return {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'wishlist_total': wishlist_total,
    }
