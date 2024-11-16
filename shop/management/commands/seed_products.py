import csv
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from shop.models import Category, Product, Review
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Removes all existing products and seeds the database with new products from a JSON file and generates a CSV for fake users'

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

        # Prepare a CSV file to store fake user details
        users_data = []

        # Remove all existing products to ensure a clean slate
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            'Deleted all existing products from the database'))

        # Process each product in the JSON data
        for product_data in products_data:
            category_name = product_data.get('category')
            category = None
            if category_name:
                category, created = Category.objects.get_or_create(
                    name=category_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Created new category: {category.name}'))

            # Create the product object
            product = Product(
                name=product_data.get('name'),
                description=product_data.get('description'),
                sku=product_data.get('sku'),
                original_price=Decimal(product_data.get('original_price', 0)),
                discount=Decimal(product_data.get('discount', 0)),
                price=Decimal(product_data.get('price', 0)),
                stock=product_data.get('stock', 0),
                image=product_data.get('image_url'),
                category=category,
                features="\n".join(product_data.get('features', [])),
            )
            product.save()  # Save the product first to generate its ID

            # Handle reviews for the product
            reviews_data = product_data.get('reviews', [])
            for review_data in reviews_data:
                user = self.get_or_create_user(
                    review_data.get('user'), users_data)

                # Create the review associated with the user and product
                review = Review(
                    user=user,
                    product=product,
                    rating=review_data.get('rating', 1),
                    comment=review_data.get('comment', ''),
                    created_at=parse_datetime(review_data.get('created_at')),
                )
                review.save()  # Save each review

            self.stdout.write(self.style.SUCCESS(
                f'Product "{product.name}" and its reviews have been successfully created'))

        # Write the CSV file with fake user details after processing all products
        self.write_users_to_csv(users_data)
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded new products, reviews, and generated fake_users.csv'))

    def get_or_create_user(self, username, users_data):
        """Checks if the user exists, otherwise creates a fake user."""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If the user doesn't exist, create a new fake user
            user = User(username=username, email=fake.email(),
                        password=fake.password())
            user.save()  # Save the newly created user
            self.stdout.write(self.style.SUCCESS(
                f'Created fake user: {username}'))

            # Store user details for CSV
            users_data.append({
                'username': username,
                'email': user.email,
                'password': user.password
            })

        return user

    def write_users_to_csv(self, users_data):
        """Writes the user data to a CSV file."""
        with open('fake_users.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(
                file, fieldnames=['username', 'email', 'password'])
            writer.writeheader()
            for user in users_data:
                writer.writerow(user)
