# shop/management/commands/generate_products.py

import json
import random
from django.core.management.base import BaseCommand # type: ignore
from faker import Faker  # type: ignore

fake = Faker()

categories = [
    "Electronics", "Accessories", "Fashion", "Computers", 
    "Sports", "Home Appliances", "Photography", "Outdoor", 
    "Toys", "Books", "Health & Beauty", "Furniture"
]

def generate_product():
    random_id = random.randint(1, 2000)
    return {
        "name": fake.word().capitalize() + " " + fake.word().capitalize(),
        "description": fake.sentence(),
        "price": round(random.uniform(5.99, 199.99), 2),
        "category": random.choice(categories),
        # Random image from Lorem Picsum API (100x100 pixels)
        "image_url": f"https://picsum.photos/200/300?random={random_id}",
        "stock": random.randint(1, 100)
    }

class Command(BaseCommand):
    help = 'Generates and saves products to a JSON file'

    def handle(self, *args, **kwargs):
        # Generate 600 products
        products = [generate_product() for _ in range(600)]

        # Save the products to a JSON file
        with open('products.json', 'w') as f:
            json.dump(products, f, indent=4)

        self.stdout.write(self.style.SUCCESS("600 products with images generated and saved to products.json"))
