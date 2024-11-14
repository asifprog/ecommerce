import json
from django.core.management.base import BaseCommand # type: ignore
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Removes all existing products and seeds the database with new products from a JSON file'

    def handle(self, *args, **kwargs):
        json_file_path = 'products.json'

        try:
            with open(json_file_path, 'r') as file:
                products_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'File {json_file_path} not found!'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                f'Error decoding JSON from {json_file_path}'))
            return

        # Remove all existing products
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            'Deleted all existing products from the database'))

        # Insert new products
        for product_data in products_data:
            # Handle category
            category_name = product_data.get('category')
            category = None
            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new category: {category.name}'))
            product = Product(
                name=product_data.get('name'),
                description=product_data.get('description'),
                price=product_data.get('price'),
                image=product_data.get('image_url'),
                stock=product_data.get('stock'),
                category=category,
            )
            product.save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded new products from JSON'))
