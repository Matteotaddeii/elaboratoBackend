from django.urls import path
from .views import ProductListView, ProductDetailView, ProductUpdateView, ProductCreateView, CategoryCreateView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('prodotto/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('prodotto/<int:pk>/modifica/', ProductUpdateView.as_view(), name='product_edit'),
    path('prodotto/nuovo/', ProductCreateView.as_view(), name='product_create'), 
    path('categoria/nuovo/', CategoryCreateView.as_view(), name='category_create'),
]