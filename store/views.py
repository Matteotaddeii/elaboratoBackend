from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.contrib.auth.decorators import login_required

class ProductListView(ListView):
    model = Product
    template_name = 'catalogo.html'
    
    # Mostra solo i prodotti attivi
    def get_queryset(self):
        return Product.objects.filter(is_active=True)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'dettagliProdotto.html'
    context_object_name = 'product' 

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'is_active', 'category']
    template_name = 'modificaProdotto.html'
    success_url = reverse_lazy('product_list')

    # Solo i Manager o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') == 'store_manager')
        )

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'is_active', 'category']
    template_name = 'modificaProdotto.html' # Uso stesso form dell'update
    success_url = reverse_lazy('product_list')

    # Solo i Manager o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') == 'store_manager')
        )

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name', 'slug'] 
    template_name = 'aggiungiCategoria.html'
    success_url = reverse_lazy('product_list') 
    
    # Solo i Manager o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') == 'store_manager')
        )

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if cart[product_id_str] < product.stock:
            cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            continue
            
    return render(request, 'carrello.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('product_list')
        
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
        except Product.DoesNotExist:
            pass
            
    request.session['cart'] = {}
    messages.success(request, "Acquisto simulato con successo!")
    return redirect('product_list')

def aggiungi_uno(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    id_str = str(product_id)
    
    if id_str in cart:
        if cart[id_str] < product.stock:
            cart[id_str] += 1
            request.session['cart'] = cart
            request.session.modified = True
        else:
            messages.error(request, f"Non puoi aggiungere altri elementi. Scorte massime raggiunte per {product.name}.")
            
    return redirect('cart_detail')


def riduci_uno(request, product_id):
    cart = request.session.get('cart', {})
    id_str = str(product_id)
    
    if id_str in cart:
        cart[id_str] -= 1
        
        if cart[id_str] <= 0:
            del cart[id_str]
            messages.info(request, "Prodotto rimosso dal carrello.")
        
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart_detail')


def elimina_prodotto(request, product_id):
    cart = request.session.get('cart', {})
    id_str = str(product_id)
    
    if id_str in cart:
        del cart[id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Prodotto eliminato dal carrello.")
        
    return redirect('cart_detail')