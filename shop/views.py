# shop/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Category, Order, OrderItem, Product
from .forms import ProductForm
from .models import Cart, CartItem
from django.db import transaction
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
  
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('product_list')

def remove_from_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
    cart_item.delete()
    return redirect('view_cart')

def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    return render(request, 'shop/cart.html', {'cart_items': cart_items})
  
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(user=request.user, total_price=sum(item.quantity * item.product.price for item in cart_items))
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            cart.cartitem_set.all().delete()
            return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'shop/checkout.html', {'cart_items': cart_items})

def create_checkout_session(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')),
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )

    return redirect(checkout_session.url)

def payment_success(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart.cartitem_set.all().delete()
    return render(request, 'shop/payment_success.html')

def payment_cancel(request):
    return render(request, 'shop/payment_cancel.html')
  
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})
  
def product_list_by_category(request, category_id=None):
    categories = Category.objects.all()
    if category_id:
        products = Product.objects.filter(category__id=category_id)
    else:
        products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products, 'categories': categories})