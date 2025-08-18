from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings 


# Create your models here.
class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=10, unique=True, blank=False)
    email = models.CharField(max_length=100 ,unique=True, blank=False)     # if any migration problem happens then it might be an possible ishu
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    
class Category(models.Model):
    cat_name = models.CharField(max_length=200)
    about_cat = models.TextField(max_length=2000)
    
    def __str__(self):
        return self.cat_name

 
    
    
class Item (models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    item_img = models.ImageField(upload_to='items/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    brand = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
      
    
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.Item.name} (x{self.quantity})"
    
    # @property
    def total(self):
        return self.Item.price * self.quantity


class ProductImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.item.name}" 
    
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE) 

    class Meta:
        unique_together = ('user', 'item')  

    def __str__(self):
        return f"{self.user} - {self.item.name}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    review = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}'s review on {self.item}"
    
    
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
    
   

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    status = models.CharField(max_length=20, default='processing')
    
    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order.order_number})"