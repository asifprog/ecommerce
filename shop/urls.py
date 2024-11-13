from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # products
    # path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    
    # cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # checkout
    path('checkout/', views.checkout, name='checkout'),    
    path('checkout/session/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # History
    path('order-history/', views.order_history, name='order_history')
]