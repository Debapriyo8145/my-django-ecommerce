from django.urls import path
from . import views

app_name = 'myapp'  

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:item_id>/', views.product_detail, name='product'),
    path('store/', views.store, name='store'), # for showing multiple products
    path('checkout/', views.checkout, name='checkout'),
    path("signup/", views.signup_view, name="signup"),
    path('login/', views.login_view, name='login'),
    path('account/', views.account_view, name='account'),
    path('logout/', views.logout_view, name='logout'),  
    path('add-to-wishlist/<int:item_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path('contact/', views.contact, name='contact'),
    path('privacy_policy/', views.privacy, name='privacy'),
    path('terms&conditions/', views.tandc, name='tandc'),
    path('about/', views.about, name='about'),
]

