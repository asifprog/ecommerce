from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Category, Order, OrderItem, Product
from .models import Cart, CartItem
from django.db import transaction
import stripe
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator

stripe.api_key = settings.STRIPE_SECRET_KEY


def register(request):
    if request.user.is_authenticated:
        return redirect('product_list')

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
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login in successful')
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid Credentials')
            return render(request, 'shop/login.html')
    else:
        form = AuthenticationForm()
        messages.error(request, 'Method failed')
    return render(request, 'shop/login.html', {'form': form})

@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


def product_list(request):
    products = Product.objects.all()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {
        'page_obj': page_obj,
        'paginator': paginator,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    print(f"Product Data ->: {product}")
    cart = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.get_or_create(
        cart=cart, product=product)
    messages.success(request, F'{cart_item} Added to cart')
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
            order = Order.objects.create(user=request.user, total_price=sum(
                item.quantity * item.product.price for item in cart_items))
            for item in cart_items:
                OrderItem.objects.create(
                    order=order, product=item.product, quantity=item.quantity)
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

    total_price = sum(
        item.quantity * item.product.price for item in cart_items)

    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart_items:
        OrderItem.objects.create(
            order=order, product=item.product, quantity=item.quantity)

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
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list_category.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'category': category if category_id else None
    })
