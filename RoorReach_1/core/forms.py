from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, SellerApplication

class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'phone', 'gender', 'location', 'address', 'password1', 'password2'
        ]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'location', 'address', 'gender', 'profile_image'
        ]

class SellerApplicationForm(forms.ModelForm):
    class Meta:
        model = SellerApplication
        fields = [
            'shop_name', 'shop_address', 'location', 'email',
            'tax_id', 'nid_number', 'category', 'application_text', 'shop_image'
        ]
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'discounted_price', 'description', 'region', 'category', 'stock', 'image']

from .models import CartItem, Order, Review, ChatMessage

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']

from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'discounted_price', 'description', 'region', 'stock', 'category', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']