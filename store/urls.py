from django.urls import path
from .views import ProductListView, ProductDetailView, ProductUpdateView, ProductCreateView, CategoryCreateView, add_to_cart, cart_detail, checkout, aggiungi_uno, riduci_uno, elimina_prodotto, ManagerDashboardView, complete_order

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('prodotto/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('prodotto/<int:pk>/modifica/', ProductUpdateView.as_view(), name='product_edit'),
    path('prodotto/nuovo/', ProductCreateView.as_view(), name='product_create'), 
    path('categoria/nuovo/', CategoryCreateView.as_view(), name='category_create'),
    path('carrello/<int:product_id>/aggiungi/', add_to_cart, name='add_to_cart'),
    path('carrello/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('carrello/<int:product_id>/aggiungi-uno/', aggiungi_uno, name='aggiungi_uno'),
    path('carrello/<int:product_id>/riduci-uno/', riduci_uno, name='riduci_uno'),
    path('carrello/<int:product_id>/elimina/', elimina_prodotto, name='elimina_prodotto'),
    path('gestione/dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('gestione/ordine/<int:order_id>/completa/', complete_order, name='complete_order'),
]