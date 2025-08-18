from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, ChangeForm, ReviewForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Cart, Wishlist, Item, ContactMessage, Category, Order, OrderItem
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from itertools import chain
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from time import timezone





def index(request):
    cart_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    wishlist_count = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    # Filter available items by categories
    laptops = Item.objects.filter(is_available=True, category__cat_name__iexact='Laptops')
    smartphones = Item.objects.filter(is_available=True, category__cat_name__iexact='Smartphones')
    cameras = Item.objects.filter(is_available=True, category__cat_name__iexact='Cameras')
    accessories = Item.objects.filter(is_available=True, category__cat_name__iexact='Accessories')
    mixed_items = chain(laptops, smartphones, cameras, accessories)
    return render(request, 'myapp/index.html', {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'laptops': laptops,
        'smartphones': smartphones,
        'cameras': cameras,
        'accessories': accessories,
        'items': mixed_items
    })

def product_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    images = item.images.all()
    reviews = item.reviews.all()
    review_count = reviews.count()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = item
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            return redirect('myapp:product', item_id=item.id)
    else:
        form = ReviewForm()

    return render(request, 'myapp/product.html', {
        'item': item,
        'reviews': reviews,
        'form': form,
        'images': images,
        'review_count': review_count
    }) 


def store(request):
    search_query = request.GET.get('query', '').strip()
    category_name = request.GET.get('category')

    # Base queryset
    items_qs = Item.objects.filter(is_available=True).select_related('category')

    # Category filter
    if category_name and category_name.lower() != 'all':
        items_qs = items_qs.filter(category__cat_name__iexact=category_name)

    # Search filter
    if search_query:
        items_qs = items_qs.filter(
            Q(name__icontains=search_query) | 
            Q(category__cat_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(items_qs, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_category': category_name,
    }
    return render(request, 'myapp/store.html', context)


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('Item')
    total_price = sum(item.Item.price * item.quantity for item in cart_items)
    
    if not cart_items.exists():
        return redirect('myapp:cart')
    
    if request.method == 'POST':
        required_fields = ['address', 'phone', 'email']
        if not all(field in request.POST for field in required_fields):
            context = {
                'cart_items': cart_items,
                'total_price': total_price,
                'total_price_in_paise': int(total_price * 100),
                'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
                'error': 'Please fill all required fields'
            }
            return render(request, 'myapp/checkout.html', context)

            
        
        try:
            # Create order
            order = Order.objects.create(
                user=request.user,
                order_number=f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}",
                payment_method=request.POST.get('payment_method', 'cod'),
                subtotal=total_price,
                shipping_cost=0,
                total_amount=total_price,
                billing_address=request.POST.get('address'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                city=request.POST.get('city', ''),
                zip_code=request.POST.get('zip_code', ''),
                country=request.POST.get('country', ''),
                order_notes=request.POST.get('order_notes', '')
            )
            
            # Create order items
            order_items = [
                OrderItem(
                    order=order,
                    product=cart_item.Item,
                    quantity=cart_item.quantity,
                    price=cart_item.Item.price,
                    total=cart_item.Item.price * cart_item.quantity
                )
                for cart_item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            
            # Clear cart
            cart_items.delete()
            
            # Send confirmation email immediately after order creation
            try:
                subject = f"Order Confirmation - #{order.order_number}"
                message = f"""Thank you for your order!
                
Order Details:
- Order Number: {order.order_number}
- Date: {order.created_at.strftime('%B %d, %Y %I:%M %p')}
- Total Amount: ₹{order.total_amount:.2f}
- Payment Method: {order.get_payment_method_display()}

Shipping Address:
{order.first_name} {order.last_name}
{order.billing_address}
{order.city}, {order.zip_code}
{order.country}

Order Items:
{"".join([f'- {item.product.name} (₹{item.price:.2f} x {item.quantity})\n' for item in order.items.all()])}

Thank you for shopping with us!
                """.strip()

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
                # You might want to log this error in production
            
            # Redirect to confirmation page
            return redirect('myapp:order_confirmation', order_id=order.id)
            
        except Exception as e:
            context = {
                'cart_items': cart_items,
                'total_price': total_price,
                'total_price_in_paise': int(total_price * 100),
                'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
                'error': f'An error occurred: {str(e)}'
            }
            return render(request, 'myapp/checkout.html', context)
    
    # GET request
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_price_in_paise': int(total_price * 100),
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'myapp/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        order.confirmed = True
        order.save()
        return redirect('myapp:order_confirmation', order_id=order.id)

    return render(request, 'myapp/order_confirmation.html', {'order': order})      
       
def privacy(request):
    return render(request, 'myapp/privacy_policy.html')

def tandc(request):
    return render(request, 'myapp/terms&conditions.html')

def about(request):
    return render(request, 'myapp/about.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('myapp:account') 

    form = AuthenticationForm(request, data=request.POST) if request.method == "POST" else AuthenticationForm()

    if request.method == "POST" and form.is_valid():
        uname = form.cleaned_data['username']
        upass = form.cleaned_data['password']
        user = authenticate(username=uname, password=upass)

        if user is not None:
            auth_login(request, user)
            return redirect('myapp:account')  

    return render(request, 'myapp/login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('myapp:login') 

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save() 
            auth_login(request, user)  
            messages.success(request, 'Your registration is successful')
            return redirect('myapp:account') 
        else:
            messages.error(request, 'Your registration was not successful')
    else:
        form = SignupForm()
    return render(request, "myapp/signup.html", {"form": form})

@login_required
def account_view(request):
    if request.method == 'POST':
        form = ChangeForm(request.POST, request.FILES, instance=request.user)  # <-- Add request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('myapp:account') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChangeForm(instance=request.user)

    return render(request, 'myapp/account.html', {'form': form})


@require_POST
def add_to_cart(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, id=item_id)
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = Cart.objects.get_or_create(user=request.user, Item=item)

        if created:
            cart_item.quantity = quantity  # Set the submitted quantity
        else:
            cart_item.quantity += quantity  # Add to existing quantity

        cart_item.save()
        return redirect('/cart')
    else:
        return redirect('/login')

def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)

        for item in cart_items:
            item.total = item.Item.price * item.quantity  # Add this line to compute per-product total

        total_price = sum(item.total for item in cart_items)
        total_price = int(total_price)

        return render(request, 'myapp/cart.html', {
            'cart_items': cart_items,
            'total_price': total_price,
        })
    else:
        return redirect('/login')
    

def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
            
        cart_item.save()
        messages.success(request, 'Cart updated successfully')
    return redirect('myapp:cart')

def remove_cart(request, id):
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(id=id, user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    else:
        return redirect('/login')
    return redirect('myapp:cart')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.select_related('item').filter(user=request.user)
    return render(request, 'myapp/wishlist.html', {'wishlist_items': wishlist_items})

def add_to_wishlist(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, id=item_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
        return redirect('/wishlist')
    else:
        return redirect('/login')
   
def remove_from_wishlist(request, item_id):
    Wishlist.objects.filter(user=request.user, item_id=item_id).delete()
    return redirect('myapp:wishlist')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            # Save to database first
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Then try to send email
            send_mail(
                f"Contact Form: {subject}",
                f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                settings.DEFAULT_FROM_EMAIL,  # Use your configured email as sender
                [settings.DEFAULT_FROM_EMAIL],  # Who receives it
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been received! We will get back to you soon.')
            
        except Exception as e:
            # This will catch both database and email errors
            messages.error(request, 'Your message was saved, but we encountered an error sending the notification. Our team will still receive it.')
            # Optional: Log the actual error for debugging
            print(f"Contact form error: {str(e)}")
    
    return render(request, 'myapp/contact.html')
