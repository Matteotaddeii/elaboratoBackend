from django.views.generic import ListView, DetailView
from .models import Product

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