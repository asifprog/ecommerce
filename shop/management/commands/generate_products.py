import json
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from faker import Faker
from faker_commerce import Provider
from django.contrib.auth.models import User

fake = Faker()
fake.add_provider(Provider)

categories = [
    "Electronics", "Accessories", "Fashion", "Computers",
    "Sports", "Home Appliances", "Photography", "Outdoor",
    "Toys", "Books", "Health & Beauty", "Furniture"
]

category_names = {
    "Electronics": [
        "Smartphone", "Bluetooth Speaker", "Laptop", "Wireless Earbuds", "Smartwatch", 
        "Tablet", "Headphones", "Portable Charger", "Gaming Console", "VR Headset"
    ],
    "Accessories": [
        "Watch Strap", "Laptop Sleeve", "Phone Case", "Sunglasses", "Backpack", 
        "Wallet", "Phone Stand", "Power Bank", "Headphone Case", "Keychain"
    ],
    "Fashion": [
        "T-Shirt", "Jeans", "Leather Jacket", "Sneakers", "Sunglasses", 
        "Handbag", "Scarf", "Dress", "Hoodie", "Belt"
    ],
    "Computers": [
        "Desktop PC", "Laptop", "Gaming Rig", "External Hard Drive", "Keyboard", 
        "Mouse", "Monitor", "Graphics Card", "CPU Cooler", "Webcam"
    ],
    "Sports": [
        "Football", "Tennis Racket", "Yoga Mat", "Dumbbells", "Soccer Cleats", 
        "Baseball Glove", "Basketball", "Running Shoes", "Resistance Bands", "Sports Water Bottle"
    ],
    "Home Appliances": [
        "Blender", "Coffee Maker", "Vacuum Cleaner", "Air Fryer", "Refrigerator", 
        "Microwave Oven", "Dishwasher", "Washing Machine", "Electric Kettle", "Toaster"
    ],
    "Photography": [
        "Camera", "Tripod", "Lens", "Camera Bag", "Lighting Kit", 
        "Camera Strap", "Drone", "Action Camera", "Flash", "Gimbal"
    ],
    "Outdoor": [
        "Tent", "Sleeping Bag", "Backpacking Backpack", "Portable Grill", "Camping Stove", 
        "Water Bottle", "Hiking Boots", "Binoculars", "Fishing Rod", "Camping Lantern"
    ],
    "Toys": [
        "Lego Set", "Action Figure", "Puzzle", "Dollhouse", "Toy Car", 
        "Board Game", "Building Blocks", "Plush Toy", "Toy Train", "RC Car"
    ],
    "Books": [
        "Fiction Novel", "Self-Help Book", "Biography", "Children's Book", "Cookbook", 
        "Science Fiction", "Fantasy Novel", "History Book", "Mystery Novel", "Poetry Collection"
    ],
    "Health & Beauty": [
        "Facial Cream", "Shampoo", "Toothpaste", "Moisturizer", "Perfume", 
        "Lip Balm", "Makeup Kit", "Hairdryer", "Nail Polish", "Sunscreen"
    ],
    "Furniture": [
        "Sofa", "Dining Table", "Office Chair", "Coffee Table", "Bookshelf", 
        "Bed Frame", "Wardrobe", "Desk", "Armchair", "Nightstand"
    ]
}

category_features = {
    "Electronics": [
        "Wireless", "Bluetooth", "Portable", "Rechargeable", "HD", "Smart", "Touchscreen", "Noise Cancelling",
        "Voice Activated", "High Definition", "Power Saving", "Compact", "Waterproof", "Fast Charging"
    ],
    "Accessories": [
        "Stylish", "Comfortable", "Durable", "High Quality", "Flexible", "Lightweight", "Portable", "Adjustable",
        "Scratch Resistant", "Eco-friendly", "Waterproof", "Premium", "Sleek"
    ],
    "Fashion": [
        "Trendy", "Comfortable", "Breathable", "Lightweight", "Sustainable", "High Fashion", "Vintage", "Luxury",
        "Elegant", "Versatile", "Fitted", "Warm", "Unique"
    ],
    "Computers": [
        "Fast", "Efficient", "High Performance", "Compact", "Expandable", "Reliable", "Multitasking", "Ergonomic",
        "High Speed", "Memory Boost", "Energy Efficient", "Customizable"
    ],
    "Sports": [
        "Lightweight", "Breathable", "Waterproof", "Durable", "High Performance", "Adjustable", "Aerodynamic",
        "High Quality", "Flexible", "Shock Absorbent", "Performance-Enhancing"
    ],
    "Home Appliances": [
        "Energy Efficient", "Quiet", "Compact", "Smart", "Durable", "Easy to Clean", "Remote Controlled",
        "Sleek Design", "Eco-friendly", "Space Saving", "Innovative", "Fast Heating"
    ],
    "Photography": [
        "HD", "Compact", "Durable", "High Resolution", "Wide Angle", "Multi-purpose", "Waterproof", "Portable",
        "Zoom Lens", "Automatic Focus", "Professional", "Lightweight"
    ],
    "Outdoor": [
        "Weatherproof", "Portable", "Durable", "Compact", "All-weather", "Heavy Duty", "Energy Efficient", "Rust-resistant",
        "Easy to Carry", "Versatile", "Multi-purpose", "Portable"
    ],
    "Toys": [
        "Fun", "Safe", "Interactive", "Educational", "Durable", "Colorful", "Non-toxic", "Creative", "Portable",
        "Unique", "Sound Activated", "Light-up"
    ],
    "Books": [
        "Informative", "Engaging", "Inspiring", "Well-Written", "Interesting", "Thought-Provoking", "Educational",
        "Motivational", "Fictional", "Non-Fictional", "Award-Winning", "Popular"
    ],
    "Health & Beauty": [
        "Organic", "Natural", "Hydrating", "Smoothing", "Rejuvenating", "Non-Greasy", "Anti-aging", "Moisturizing",
        "Fragrance-free", "Cruelty-free", "Vegan", "SPF Protection"
    ],
    "Furniture": [
        "Stylish", "Comfortable", "Durable", "Space Saving", "Modular", "Ergonomic", "Adjustable", "Contemporary",
        "Multi-purpose", "Compact", "Easy to Assemble", "Sustainable"
    ]
}


def generate_product():
    random_id = random.randint(1, 2000)
    original_price = Decimal(round(random.uniform(20.00, 500.00), 2))
    discount_percentage = Decimal(
        round(random.uniform(0, min(50, float(original_price))), 2))
    discount = (original_price * discount_percentage) / 100

    category = random.choice(categories)
    features = random.sample(category_features.get(
        category, []), k=random.randint(3, 6))

    description = generate_description(features)

    reviews = [generate_review() for _ in range(5)]

    return {
        "name": generate_product_name(category),
        "description": description,
        "sku": fake.unique.ean(length=13),
        "original_price": float(original_price),
        "discount": float(discount),
        "price": float(original_price - discount),
        "image_url": f"https://picsum.photos/200/300?random={random_id}",
        "category": category,
        "stock": random.randint(1, 100),
        "features": features,
        "reviews": reviews
    }

def generate_product_name(category):
    if category in category_names:
        return random.choice(category_names[category])
    else:
        return fake.ecommerce_name()

def generate_review():
    """
    Generate a random review with a rating and optional comment.
    """
    rating = random.randint(1, 5)
    comment = fake.text(max_nb_chars=100)

    user_name = fake.user_name()

    created_at = fake.date_this_year()

    created_at_str = created_at.strftime("%Y-%m-%d") if created_at else None

    return {
        "user": user_name,
        "rating": rating,
        "comment": comment,
        "created_at": created_at_str
    }



def generate_description(features):
    """
    Generate a random product description based on the provided features.
    The description should sound like a natural eCommerce description.
    """
    templates = [
        "This product is perfect for {usage}. It features {feature1}, {feature2}, and {feature3} for enhanced performance.",
        "Experience {feature1} with this amazing product. Ideal for {usage}, it also includes {feature2} and {feature3}.",
        "Designed for {usage}, this product offers {feature1}, {feature2}, and {feature3} to meet all your needs.",
        "With {feature1} and {feature2}, this product ensures {usage} like never before. Plus, it includes {feature3} for extra convenience.",
        "Perfect for {usage}, this product comes with {feature1}, {feature2}, and {feature3} for a truly unique experience.",
        "Elevate your {usage} with this innovative product, featuring {feature1}, {feature2}, and {feature3} for ultimate convenience.",
        "This product combines {feature1}, {feature2}, and {feature3} to deliver superior performance, making it ideal for {usage}.",
        "Get the most out of your {usage} with this product, which includes {feature1}, {feature2}, and {feature3} for optimal results.",
        "Whether you're {usage}, this product will exceed your expectations with its {feature1}, {feature2}, and {feature3}.",
        "Transform your {usage} with the power of {feature1}, {feature2}, and {feature3}—this product has it all.",
        "Achieve the perfect {usage} with this versatile product, packed with {feature1}, {feature2}, and {feature3} for everyday use.",
        "Take your {usage} to the next level with this sleek product, featuring {feature1}, {feature2}, and {feature3}.",
        "Packed with {feature1}, {feature2}, and {feature3}, this product is perfect for anyone looking to {usage}.",
        "This product is a game-changer for {usage}, offering {feature1}, {feature2}, and {feature3} to ensure you get the most out of it.",
        "Unleash your full potential with this product, featuring {feature1}, {feature2}, and {feature3} to help with your {usage}.",
        "Maximize your {usage} with this top-rated product, designed with {feature1}, {feature2}, and {feature3} in mind.",
        "Built for {usage}, this product provides {feature1}, {feature2}, and {feature3} to enhance your experience.",
        "This product is designed to make your {usage} simpler and more enjoyable, thanks to {feature1}, {feature2}, and {feature3}.",
        "Perfect for {usage}, this product combines {feature1}, {feature2}, and {feature3} for a streamlined experience.",
        "Ready to enhance your {usage}? This product includes {feature1}, {feature2}, and {feature3} for superior results."
    ]


    template = random.choice(templates)

    feature1, feature2, feature3 = random.sample(features, 3)

    description = template.format(
        usage="everyday use",
        feature1=feature1,
        feature2=feature2,
        feature3=feature3,
        product_name="this product"
    )

    return description


class Command(BaseCommand):
    help = 'Generates and saves products with reviews to a JSON file'

    def handle(self, *args, **kwargs):
        products = [generate_product() for _ in range(2000)]

        with open('products.json', 'w') as f:
            json.dump(products, f, indent=4)

        self.stdout.write(self.style.SUCCESS(
            "2000 products with reviews generated and saved to products_with_reviews.json"))
