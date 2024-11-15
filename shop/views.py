from django.shortcuts import redirect
from .models import Cart, Product, CartItem
from django.shortcuts import render
from shop.models import Product, Cart, CartItem
from django.shortcuts import redirect, get_object_or_404
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
            # Adding items to cart
            if request.user.is_authenticated:
                session_cart = request.session.get('cart', {})
                if session_cart:
                    cart, created = Cart.objects.get_or_create(
                        user=request.user)

                    for product_id, item in session_cart.items():
                        product = get_object_or_404(Product, id=product_id)
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart, product=product)

                        if not created:
                            cart_item.quantity += item['quantity']
                        else:
                            cart_item.quantity = item['quantity']
                        cart_item.save()

                    del request.session['cart']

                messages.success(
                    request, 'Cart items migrated to your account')
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
    products = Product.objects.all().order_by('id')

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

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.save()

        messages.success(request, f'{product.name} added to cart')

    else:
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {'quantity': 1, 'name': product.name}

        request.session['cart'] = cart

        messages.success(request, f'{product.name} added to cart (session)')

    return redirect('product_list')


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)

        cart_item = CartItem.objects.filter(
            cart=cart, product__id=product_id).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(
                    request, f'{cart_item.product.name} quantity decreased by 1.')
            else:
                cart_item.delete()
                messages.success(
                    request, f'{cart_item.product.name} removed from cart.')
        else:
            messages.error(request, 'Item not found in cart.')

    else:
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            product_name = cart[str(product_id)]["name"]

            if cart[str(product_id)]['quantity'] > 1:
                cart[str(product_id)]['quantity'] -= 1
                request.session['cart'] = cart
                messages.success(
                    request, f'{product_name} quantity decreased by 1.')
            else:
                del cart[str(product_id)]
                request.session['cart'] = cart
                messages.success(request, f'{product_name} removed from cart.')
        else:
            messages.error(request, 'Item not found in cart.')

    return redirect('view_cart')


def view_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        cart_items_with_details = [
            {
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'description': item.product.description,
                    'price': item.product.price,
                    'image': item.product.image,
                    'category': item.product.category.name if item.product.category else None,
                    'stock': item.product.stock
                },
                'quantity': item.quantity,
                'subtotal': item.quantity * item.product.price
            }
            for item in cart_items
        ]
    else:
        cart = request.session.get('cart', {})
        cart_items_with_details = [
            {
                'product': {
                    'id': Product.objects.get(id=product_id).id,
                    'name': item['name'],
                    'description': Product.objects.get(id=product_id).description,
                    'price': Product.objects.get(id=product_id).price,
                    'image': Product.objects.get(id=product_id).image,
                    'category': Product.objects.get(id=product_id).category.name if Product.objects.get(id=product_id).category else None,
                    'stock': Product.objects.get(id=product_id).stock
                },
                'quantity': item['quantity'],
                'subtotal': item['quantity'] * Product.objects.get(id=product_id).price
            }
            for product_id, item in cart.items()
        ]

    total_items_in_cart = get_cart_total_items(request)
    total_price = sum(item['subtotal'] for item in cart_items_with_details)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items_with_details,
        'total_items_in_cart': total_items_in_cart,
        'total_price': total_price
    })


def get_cart_total_items(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        total_items = sum([item.quantity for item in cart.cartitem_set.all()])
    else:
        cart = request.session.get('cart', {})
        total_items = sum(item['quantity'] for item in cart.values())

    return total_items


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
