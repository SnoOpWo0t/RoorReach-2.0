from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    CustomUser, Category, Product, CartItem,
    Order, Review, ChatMessage, SellerApplication
)
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_seller_approved']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'profile_image', 'user_type', 'location', 'address', 'gender', 'is_seller_approved')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(ChatMessage)
admin.site.register(SellerApplication)
