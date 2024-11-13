import json
import random
from faker import Faker # type: ignore

fake = Faker()

categories = [
    "Electronics", "Accessories", "Fashion", "Computers", 
    "Sports", "Home Appliances", "Photography", "Outdoor", 
    "Toys", "Books", "Health & Beauty", "Furniture"
]

def generate_product():
    return {
        "name": fake.word().capitalize() + " " + fake.word().capitalize(),
        "description": fake.sentence(),
        "price": round(random.uniform(5.99, 199.99), 2),
        "category": random.choice(categories),
        # Random image from Lorem Picsum API (100x100 pixels)category
        "image_url": f"https://picsum.photos/200/300?random={random.randint(1, 1000)}",
        "stock": random.randint(1, 100)
    }

# Generate 300 products
products = [generate_product() for _ in range(300)]  # Generate 300 products

# Save the products to a JSON file
with open('products.json', 'w') as f:
    json.dump(products, f, indent=4)

print("300 products with images generated and saved to products.json")