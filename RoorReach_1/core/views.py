from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserRegistrationForm, ProfileUpdateForm, SellerApplicationForm
from .models import CustomUser, SellerApplication
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Product, Category

from django.db.models import Q, Count
from .models import Product, Category

from django.db.models import Q, Count, Avg  # ← make sure Avg is imported

from django.db.models import Q, Count, Avg
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Count, Avg
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Count, Avg
from decimal import Decimal, InvalidOperation
from .models import Product, Category

def home(request):
    query = request.GET.get('q', '').strip()
    region = request.GET.get('region', '').strip()
    stock = request.GET.get('stock', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    sort = request.GET.get('sort', '')
    category_id = request.GET.get('category', '')

    # Step 1: Start from the base QuerySet
    base_products = Product.objects.all()

    # Step 2: Apply filters
    if query:
        base_products = base_products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if region:
        base_products = base_products.filter(region__icontains=region)

    if stock == "in":
        base_products = base_products.filter(stock__gt=0)
    elif stock == "out":
        base_products = base_products.filter(stock__lte=0)

    if category_id:
        base_products = base_products.filter(category_id=category_id)

    try:
        if min_price:
            base_products = base_products.filter(price__gte=Decimal(min_price))
        if max_price:
            base_products = base_products.filter(price__lte=Decimal(max_price))
    except (ValueError, InvalidOperation):
        pass

    if sort == "asc":
        base_products = base_products.order_by('price')
    elif sort == "desc":
        base_products = base_products.order_by('-price')

    # Step 3: Only after all filters, apply annotation
    products = base_products.annotate(avg_rating=Avg('reviews__rating')).distinct()

    # Step 4: Top categories
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:5]

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
    })


from django.contrib.auth import login  # 👈 import login

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'buyer'  # Default
            user.save()

            login(request, user)  # 👈 Auto-login after saving the user

            messages.success(request, 'Account created successfully. You are now logged in.')
            return redirect('home')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ProfileUpdateForm

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')  # ← redirects to homepage
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {'form': form})


@login_required
def apply_seller(request):
    if SellerApplication.objects.filter(user=request.user).exists():
        messages.info(request, "You already applied.")
        return redirect('profile')

    if request.method == 'POST':
        form = SellerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Application submitted for review.")
            return redirect('home')
    else:
        form = SellerApplicationForm()
    return render(request, 'apply_seller.html', {'form': form})


# Admin view to approve sellers (dashboard will come later)
from django.contrib.admin.views.decorators import staff_member_required
from .models import SellerApplication, CustomUser
@staff_member_required
def seller_requests(request):
    requests = SellerApplication.objects.filter(approved=False)
    return render(request, 'seller_requests.html', {'requests': requests})

@staff_member_required
def approve_seller(request, pk):
    application = SellerApplication.objects.get(pk=pk)
    user = application.user

    # ✅ Correctly set user to seller
    user.user_type = 'seller'
    user.is_seller_approved = True
    user.save()

    # ✅ Mark the application as approved
    application.approved = True
    application.save()

    return redirect('seller_requests')

@staff_member_required
def reject_seller(request, pk):
    application = SellerApplication.objects.get(pk=pk)
    application.delete()
    return redirect('seller_requests')

from .forms import ProductForm
from .models import Product, Order, Review
from django.contrib import messages

@login_required
def sell_zone(request):
    if not request.user.is_authenticated or not request.user.is_seller():
        return redirect('home')

    products = Product.objects.filter(seller=request.user)
    return render(request, 'sell_zone.html', {'products': products})

@login_required
def add_product(request):
    if not request.user.is_seller():
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('sell_zone')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id, seller=request.user)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('sell_zone')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Order

@login_required
def seller_orders(request):
    if not request.user.is_seller():
        return redirect('home')

    status_filter = request.GET.get('status')  # 'pending', 'confirmed', etc.

    orders = Order.objects.filter(product__seller=request.user).order_by('-ordered_at')

    if status_filter in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        orders = orders.filter(status=status_filter)

    return render(request, 'seller_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
    })



@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, product__seller=request.user)
    order.status = 'cancelled'
    order.save()
    messages.success(request, f"Order #{order.id} cancelled.")
    return redirect('seller_orders')

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, CustomUser, ORDER_STATUS


def update_order_status(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id, product__seller=user)

    if not user.is_seller():
        return JsonResponse({'success': False, 'message': "Unauthorized seller"}, status=403)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ORDER_STATUS):
            order.status = new_status
            order.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': new_status,
                    'message': f"Order #{order.id} status updated to {new_status}."
                })

            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
        return redirect('seller_orders')


from .models import Product, CartItem, Order, Review, ChatMessage
from .forms import ReviewForm, ChatMessageForm

from django.shortcuts import redirect, get_object_or_404
from .models import Product, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ❌ Prevent users from adding their own product
    if request.user == product.seller:
        messages.warning(request, "You cannot add your own product to the cart.")
        return redirect('product_detail', pk=product_id)

    # ❌ Prevent adding out-of-stock products
    if product.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect('product_detail', pk=product_id)

    # ✅ Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, "You've reached the maximum available stock.")
            return redirect('cart')
    else:
        cart_item.quantity = 1
        cart_item.save()

    # ✅ Optionally reduce stock at time of adding to cart (not typical — usually at checkout)
    # product.stock -= 1
    # product.save()

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    if request.method == 'POST':
        item.quantity = int(request.POST.get('quantity'))
        item.save()
    return redirect('cart')

@login_required
def remove_cart_item(request, item_id):
    CartItem.objects.get(id=item_id, user=request.user).delete()
    return redirect('cart')


@login_required
def place_order(request):
    cart_items = CartItem.objects.select_related('product').filter(user=request.user)
    subtotal = sum(item.total_price() for item in cart_items)
    shipping_cost = 60
    total = subtotal + shipping_cost

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # Get shipping details
        shipping_address = f"""
Name: {request.POST.get('full_name')}
Phone: {request.POST.get('phone')}
Email: {request.POST.get('email')}
Address: {request.POST.get('shipping_address')}
Payment Method: {request.POST.get('payment_method', 'Not specified')}
"""
        # Check stock availability
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f"Not enough stock for '{item.product.name}'. Only {item.product.stock} left in stock."
                )
                return redirect('cart')

        # Create orders and update stock
        for item in cart_items:
            Order.objects.create(
                buyer=request.user,
                product=item.product,
                quantity=item.quantity,
                shipping_address=shipping_address,
                status='pending',
                payment_status=False
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart and redirect
        cart_items.delete()
        messages.success(request, "Order placed successfully! Track your order status in the Orders page.")
        return redirect('order_tracking')

    return render(request, 'place_order.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total
    })


@login_required
def order_tracking(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'order_tracking.html', {'orders': orders})

from django.shortcuts import render, get_object_or_404
from .models import Product
from .forms import ReviewForm

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Review
from .forms import ReviewForm

@login_required
def submit_review(request, pk):
    product = get_object_or_404(Product, id=pk)

    # ✅ Only allow review if buyer purchased the product
    if not Order.objects.filter(buyer=request.user, product=product).exists():
        return redirect('product_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)

        # 🔥 Extract rating from hidden input (JS-powered)
        rating = request.POST.get('rating')

        # ✅ Validate rating is 1–5
        if form.is_valid() and rating in ['1', '2', '3', '4', '5']:
            review = form.save(commit=False)
            review.reviewer = request.user
            review.product = product
            review.rating = int(rating)  # ← set manually from hidden input
            review.save()

    return redirect('product_detail', pk=pk)




from django.http import HttpResponse
from django.db.models import Q
from .models import ChatMessage, Product
from .forms import ChatMessageForm

def product_chat(request, pk):
    product = get_object_or_404(Product, id=pk)
    form = ChatMessageForm(request.POST or None)

    # Determine who the other user is (ensure consistent pairing)
    if request.user == product.seller:
        buyer = ChatMessage.objects.filter(product=product).exclude(buyer=None).order_by('-timestamp').first()
        buyer_user = buyer.buyer if buyer else None
    else:
        buyer_user = request.user

    if form.is_valid():
        msg = form.save(commit=False)
        msg.product = product

        # Prevent contact info sharing
        if any(word in msg.message.lower() for word in ['phone', 'email', '@', 'contact']):
            return HttpResponse("Sharing contact info is not allowed.")

        if request.user == product.seller and buyer_user:
            msg.seller = request.user
            msg.buyer = buyer_user
        else:
            msg.buyer = request.user
            msg.seller = product.seller

        msg.save()
        return redirect('product_chat', pk=pk)

    # Show messages related to this product between this seller and buyer
    messages = ChatMessage.objects.filter(
        product=product
    ).filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by("timestamp")

    return render(request, 'product_chat.html', {
        'product': product,
        'form': form,
        'messages': messages,
        'user': request.user
    })


from decimal import Decimal, InvalidOperation

def search_products(request):
    products = Product.objects.all()

    query = request.GET.get('q', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    region = request.GET.get('region', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', '')

    # Search filter
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    # Price filter (safely parse to decimal)
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except InvalidOperation:
        pass  # Invalid input skipped silently (you could flash an error message instead)

    # Region filter
    if region:
        products = products.filter(region__icontains=region)

    # Stock filter
    if stock == 'in':
        products = products.filter(stock__gt=0)
    elif stock == 'out':
        products = products.filter(stock=0)

    # Sort
    if sort == 'low':
        products = products.order_by('price')
    elif sort == 'high':
        products = products.order_by('-price')

    return render(request, 'search.html', {'products': products})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import ProductForm, CategoryForm

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('sell_zone')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form})

from django.utils.http import urlencode

@login_required
def add_category(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('sell_zone')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {
        'form': form,
        'next': next_url
    })


def about(request):
    return render(request, 'about.html')
def all_policies(request):
    return render(request, 'All_policy.html')

def terms_conditions(request):
        return render(request, 'terms_conditions.html')

def categories(request):
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    # Annotate categories with product count
    categories = categories.annotate(product_count=Count('product')).order_by('name')

    return render(request, 'all_categories.html', {
        'categories': categories,
        'search_query': search_query
    })

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.select_related('seller').filter(category=category)

    # Apply any filters from the request
    query = request.GET.get('q', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    region = request.GET.get('region', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', '')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, InvalidOperation):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, InvalidOperation):
            pass

    if region:
        products = products.filter(region__icontains=region)

    if stock == "in":
        products = products.filter(stock__gt=0)
    elif stock == "out":
        products = products.filter(stock__lte=0)

    # Default sorting by newest if no sort parameter
    if sort == "asc":
        products = products.order_by('price', '-id')
    elif sort == "desc":
        products = products.order_by('-price', '-id')
    else:
        products = products.order_by('-id')

    context = {
        'category': category,
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'category_products.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def cancel_user_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if order.status.lower() in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.warning(request, "This order can no longer be cancelled.")

    return redirect('order_tracking')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage, Product


@login_required
def seller_messages(request):
    if not request.user.is_seller():
        return redirect('home')

    # Get all products of the seller
    products = Product.objects.filter(seller=request.user)
    product_messages = []

    # For each product, get its messages
    for product in products:
        # Get messages related to the product and order by timestamp
        messages = ChatMessage.objects.filter(
            product=product
        ).filter(
            Q(seller=request.user) | Q(buyer__isnull=False, product__seller=request.user)
        ).order_by('timestamp')

        if messages.exists():
            product_messages.append({
                'product': product,
                'messages': messages
            })

    return render(request, 'seller_messages.html', {
        'product_messages': product_messages
    })


from django.shortcuts import render, get_object_or_404
from .models import Order, ChatMessage

@login_required
def buyer_messages_in_orders(request):
    if not request.user.is_buyer():  # Ensure only buyers can access this view
        return redirect('home')

    # Get all orders related to the buyer
    orders = Order.objects.filter(buyer=request.user)
    order_messages = []

    # For each order, get its product and messages
    for order in orders:
        product = order.product
        messages = ChatMessage.objects.filter(product=product).order_by('timestamp')
        if messages.exists():
            order_messages.append({
                'order': order,
                'product': product,
                'messages': messages
            })

    # Pass the order messages to the template
    return render(request, 'buyer_order_messages.html', {
        'order_messages': order_messages
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

@login_required
def view_messages(request):
    if request.user.is_authenticated:
        # Get all messages for the logged-in user (buyer/seller)
        messages = ChatMessage.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ).order_by('-timestamp')  # You can modify sorting as needed

        return render(request, 'view_messages.html', {'messages': messages})
    else:
        return redirect('login')  # Or handle as per your app flow

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, ChatMessage

@login_required
def buyer_messages_in_orders(request):
    if not request.user.is_buyer():  # Ensure only buyers can access this view
        return redirect('home')

    # Get all orders related to the buyer
    orders = Order.objects.filter(buyer=request.user)
    order_messages = []

    # For each order, get its product and messages
    for order in orders:
        product = order.product
        # Get all messages related to this product for this buyer
        messages = ChatMessage.objects.filter(product=product).order_by('timestamp')
        if messages.exists():
            order_messages.append({
                'order': order,
                'product': product,
                'messages': messages
            })

    # Pass the order messages to the template
    return render(request, 'buyer_order_messages.html', {
        'order_messages': order_messages
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ChatMessage
from django.contrib import messages

@login_required
def reply_to_message(request, product_id):
    # Get the product to which the message belongs
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        reply_content = request.POST.get('reply')  # The reply from the seller

        # Create a new message in the ChatMessage model
        new_message = ChatMessage(
            product=product,
            seller=request.user,  # Assuming the seller is replying
            message=reply_content
        )
        new_message.save()

        # Optionally, you can send a success message
        messages.success(request, 'Your reply has been sent.')

        return redirect('seller_messages')  # Redirect back to the seller's message page for that product


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, ChatMessage
from django.contrib import messages

@login_required
def buyer_reply_to_message(request, product_id):
    # Ensure the user is a buyer
    if not request.user.is_buyer():
        return redirect('home')

    # Get the product to which the message belongs
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        reply_content = request.POST.get('reply')  # The reply from the buyer

        # Create a new message in the ChatMessage model
        new_message = ChatMessage(
            product=product,
            buyer=request.user,  # Assuming the buyer is replying
            message=reply_content
        )
        new_message.save()

        # Optionally, you can send a success message
        messages.success(request, 'Your reply has been sent.')

        return redirect('buyer_messages_in_orders')  # Redirect back to the buyer's messages page for that order

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser  # Ensure you import your CustomUser model

@login_required
def apply_seller_status(request):
    # Check if the user is already a seller
    if request.user.user_type == 'seller':
        # If the user is already a seller, render the 'already_seller' template
        return render(request, 'already_seller.html')
    else:
        # Redirect to the seller application page if the user is not a seller
        return redirect('apply_seller')  # Replace 'apply_seller' with your actual seller application page URL name

