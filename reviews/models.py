from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from store.models import Product

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Voto"
    )
    comment = models.TextField(max_length=1000, verbose_name="Commento")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recensione di {self.user.username} per {self.product.name} ({self.rating}★)"