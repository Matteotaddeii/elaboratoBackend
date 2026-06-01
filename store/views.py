from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'catalogo.html'
    
    # Filtriamo per mostrare solo i prodotti attivi
    def get_queryset(self):
        return Product.objects.filter(is_active=True)