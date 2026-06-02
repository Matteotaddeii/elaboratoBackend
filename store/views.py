from django.views.generic import ListView, DetailView
from .models import Product
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

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
            user.is_superuser or 
            str(getattr(user, 'role', '')).lower() in ['store_manager']
        )