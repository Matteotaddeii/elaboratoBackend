from django.urls import path
from . import views

urlpatterns = [
    path('aggiungi/<int:product_id>/', views.add_review, name='add_review'),
    path('cancella/<int:review_id>/', views.delete_review, name='delete_review'),
    path('modifica/<int:review_id>/', views.edit_review, name='edit_review'),
]