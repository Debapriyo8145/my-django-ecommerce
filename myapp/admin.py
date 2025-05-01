from django.contrib import admin 
from django.utils.html import format_html
from .models import Category, Item, ProductImage

# Admin Panel Branding
admin.site.site_header = "E-Commerce Admin Panel"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Welcome to Electro's E-Commerce Dashboard"

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_name', 'about_cat')




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    def product_img(self, obj):
        if obj.item_img:
            return format_html('<img src="{}" width="100" height="100" />', obj.item_img.url)
        return "No Image"

    product_img.short_description = 'Image'

    list_display = ('name', 'price', 'category', 'product_img', 'is_available', 'updated_at', 'brand')
