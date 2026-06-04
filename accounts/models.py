from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Definiamo le costanti per i ruoli richiesti dalla traccia
    CUSTOMER = 'customer'
    STORE_MANAGER = 'store_manager'
    WAREHOUSE_WORKER = 'warehouse_worker'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (STORE_MANAGER, 'Store Manager'),
        (WAREHOUSE_WORKER, 'Warehouse Worker'),
    ]
    
    # Campo personalizzato per salvare il ruolo nel database
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=CUSTOMER,
        help_text="Ruolo dell'utente all'interno dell'e-commerce"
    )

    def is_manager(self):
        return self.role == self.STORE_MANAGER

    def is_warehouse(self):
        return self.role == self.WAREHOUSE_WORKER