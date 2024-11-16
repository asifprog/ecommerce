from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    features = models.TextField(blank=True, null=True)
    reviews = models.ManyToManyField(
        'Review', blank=True, related_name='products')

    def clean(self):
        """Ensure discount is not greater than original price, and price is non-negative."""
        if self.discount > self.original_price:
            raise ValidationError(
                "Discount cannot be greater than the original price.")

        if self.original_price - self.discount < 0:
            raise ValidationError("Price after discount cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()

        self.price = self.original_price - Decimal(self.discount)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
