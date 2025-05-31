from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ---------------------------
# 🔐 Custom User Model
# ---------------------------

USER_TYPES = (
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
    ('admin', 'Admin'),
)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='buyer')
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')
    location = models.CharField(max_length=100)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    is_seller_approved = models.BooleanField(default=False)

    def is_buyer(self):
        return self.user_type == 'buyer'

    def is_seller(self):
        return self.user_type == 'seller' and self.is_seller_approved

    def is_admin(self):
        return self.is_superuser

# ---------------------------
# 🏷 Category
# ---------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# ---------------------------
# 📦 Product
# ---------------------------

class Product(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'seller'})
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    region = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='products/')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # average rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.seller.username}"

# ---------------------------
# 🛒 Cart Item
# ---------------------------

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        price = self.product.discounted_price or self.product.price
        return self.quantity * price

    def __str__(self):
        return f"{self.product.name} x{self.quantity} for {self.user.username}"

# ---------------------------
# 🧾 Orders
# ---------------------------

ORDER_STATUS = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
)

class Order(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(default=timezone.now)

    def total_price(self):
        price = self.product.discounted_price or self.product.price
        return self.quantity * price

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

# ---------------------------
# ⭐ Product Review
# ---------------------------

class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐☆☆☆☆'),
        (2, '⭐⭐☆☆☆'),
        (3, '⭐⭐⭐☆☆'),
        (4, '⭐⭐⭐⭐☆'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)  # ← Updated
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}/5 by {self.reviewer.username} on {self.product.name}"


# ---------------------------
# 💬 Chat System (Buyer ↔ Seller)
# ---------------------------

class ChatMessage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(CustomUser, related_name='buyer_messages', on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(CustomUser, related_name='seller_messages', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.buyer if self.buyer else self.seller
        return f"Msg from {sender.username} about {self.product.name}"


# ---------------------------
# 🏪 Seller Application (Pending Approval)
# ---------------------------

class SellerApplication(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=150)
    shop_address = models.TextField()
    location = models.CharField(max_length=100)
    email = models.EmailField()
    tax_id = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    nid_number = models.CharField(max_length=30)
    application_text = models.TextField()
    shop_image = models.ImageField(upload_to='seller_applications/', null=True, blank=True)
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s seller application"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1 to 5
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}/5 by {self.reviewer.username} on {self.product.name}"

    def is_verified_buyer(self):
        return Order.objects.filter(buyer=self.reviewer, product=self.product,
                                    status__in=['confirmed', 'shipped', 'delivered']).exists()

