import json
from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with products from a JSON file'

    def handle(self, *args, **kwargs):
        json_file_path = 'products.json'
        
        try:
            with open(json_file_path, 'r') as file:
                products_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {json_file_path} not found!'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decoding JSON from {json_file_path}'))
            return

        for product_data in products_data:
            product = Product(
                name=product_data.get('name'),
                description=product_data.get('description'),
                price=product_data.get('price'),
                stock=product_data.get('stock')
            )
            product.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded products from JSON'))
