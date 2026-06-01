from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# Questo permette di vedere i prodotti ordinati direttamente dentro la pagina dell'ordine principale
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} # Genera lo slug in automatico mentre scrivi il nome!

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'is_active']
    list_filter = ['is_active', 'category']
    list_editable = ['price', 'stock', 'is_active'] # Permette di modificarli al volo dalla lista

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'is_completed', 'total_price']
    list_filter = ['is_completed', 'created_at']
    inlines = [OrderItemInline]