from django.views.generic import ListView, DetailView
from .models import Product, Category, Order, OrderItem
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from reviews.forms import ReviewForm

class ProductListView(ListView):
    model = Product
    template_name = 'catalogo.html'

    # Impaginazione 6 prodotti per pagina 
    paginate_by = 6
    
    def get_queryset(self):
        # Inizialmente vede tutti i prodotti
        queryset = super().get_queryset()
        
        # Filtro is_active (default True, gestibile da gestori/superuser)
        user = self.request.user
        
        if user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') in ['store_manager', 'warehouse_worker']):
            active_filter = self.request.GET.get('active_filter', 'active')
            if active_filter == 'active':
                queryset = queryset.filter(is_active=True)
            elif active_filter == 'inactive':
                queryset = queryset.filter(is_active=False)
        else:
            # Clienti vedono solo i prodotti attivi
            queryset = queryset.filter(is_active=True)
            
        # Ricerca per nome o descrizione
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
            
        # Filtro per categoria
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        # Passo l'elenco di tutte le categorie per poterle mostrare nel menu di filtro
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        context['active_filter'] = self.request.GET.get('active_filter', 'active')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'dettagliProdotto.html'
    context_object_name = 'product' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        return context

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'is_active', 'category']
    template_name = 'modificaProdotto.html'
    success_url = reverse_lazy('product_list')

    # Solo i Manager, i Magazzinieri o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') in ['store_manager', 'warehouse_worker'])
        )

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'is_active', 'category']
    template_name = 'modificaProdotto.html' # Uso stesso form dell'update
    success_url = reverse_lazy('product_list')

    # Solo i Manager, i Magazzinieri o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') in ['store_manager', 'warehouse_worker'])
        )

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name', 'slug'] 
    template_name = 'aggiungiCategoria.html'
    success_url = reverse_lazy('product_list') 
    
    # Solo i Manager, i Magazzinieri o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') in ['store_manager', 'warehouse_worker'])
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
    
    cart_items = []
    total_price = 0
    
    # Verifico disponibilità prodotti
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        if product.stock < quantity:
            messages.error(request, f"Ci dispiace, lo stock di '{product.name}' è cambiato nel frattempo. Rimangono solo {product.stock} pezzi.")
            return redirect('cart_detail')
        
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })

    # Creo l'ordine e scalo disponibilità
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            is_completed=False
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            
            # Scalo disponibilità
            product = item['product']
            product.stock -= item['quantity']
            product.save()

    # Svuoto il carrello
    request.session['cart'] = {}
    
    messages.success(request, f"Acquisto completato con successo! È stato generato l'Ordine #{order.id}.")
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

class ManagerDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'pannelloGestore.html'
    context_object_name = 'orders'
    ordering = ['-id']
    paginate_by = 20

    # Solo i Manager o i Superuser possono accedere
    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') == 'store_manager')
        )

@login_required
def complete_order(request, order_id):
    user = request.user
    if not (user.is_superuser or (user.is_authenticated and getattr(user, 'role', '') == 'store_manager')):
        messages.error(request, "Accesso negato.")
        return redirect('product_list')
        
    order = get_object_or_404(Order, id=order_id)
    order.is_completed = True
    order.status = 'shipped'
    order.save()
    
    messages.success(request, f"Ordine #{order.id} segnato come completato!")
    return redirect('manager_dashboard')

@login_required
def userOrders(request):
    # Prendo solo ordini in cui l'utente è l'utente loggato della richiesta
    orders_list = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ordiniUtente.html', {'orders': page_obj})

@login_required
def warehouse_dashboard(request):
    if getattr(request.user, 'role', '') != 'warehouse_worker' and not request.user.is_superuser:
        messages.error(request, "Accesso negato. Questa dashboard è riservata alla logistica.")
        return redirect('product_list')
        
    orders_to_ship = Order.objects.filter(status__in=['pending', 'processing']).order_by('created_at')
    
    products = Product.objects.all().order_by('name')
    
    return render(request, 'gestioneMagazzino.html', {
        'orders': orders_to_ship,
        'products': products
    })

@login_required
def warehouse_ship_order(request, order_id):
    if getattr(request.user, 'role', '') != 'warehouse_worker' and not request.user.is_superuser:
        messages.error(request, "Accesso negato.")
        return redirect('product_list')
        
    order = get_object_or_404(Order, id=order_id)
    order.status = 'shipped'
    order.is_completed = True
    order.save()
    
    messages.success(request, f"Ordine #{order.id} contrassegnato come SPEDITO correttamente!")
    return redirect('warehouse_dashboard')

@login_required
def warehouse_update_stock(request, product_id):
    if getattr(request.user, 'role', '') != 'warehouse_worker' and not request.user.is_superuser:
        messages.error(request, "Accesso negato.")
        return redirect('product_list')
        
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_stock = request.POST.get('stock')
        is_active = request.POST.get('is_active') == 'true'
        
        if new_stock is not None:
            product.stock = int(new_stock)
            product.is_active = is_active
            product.save()
            messages.success(request, f"Stock del prodotto '{product.name}' aggiornato.")
            
    return redirect('warehouse_dashboard')    