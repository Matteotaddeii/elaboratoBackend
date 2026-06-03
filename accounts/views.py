from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomerRegistrationForm, UserProfileForm
from django.core.paginator import Paginator


def register_view(request):
    if request.user.is_authenticated:
        return redirect('product_list')
        
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registrazione completata! Benvenuto sullo store, {user.username}!")
            return redirect('product_list')
    else:
        form = CustomerRegistrationForm()
        
    return render(request, 'iscrizioneUtente.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dati del profilo aggiornati con successo!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'profiloUtente.html', {'form': form})


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'cambiaPassword.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, "Password modificata con successo!")
        return super().form_valid(form)


@login_required
def manager_users_list(request):
    if not (request.user.is_manager() or request.user.is_superuser):
        messages.error(request, "Accesso negato. Non hai i permessi per gestire gli utenti.")
        return redirect('product_list')
        
    users_list = CustomUser.objects.filter(is_superuser=False).order_by('username')
    paginator = Paginator(users_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestioneUtenti.html', {'page_obj': page_obj})


@login_required
def toggle_user_status(request, user_id):
    if not (request.user.is_manager() or request.user.is_superuser):
        messages.error(request, "Accesso negato.")
        return redirect('product_list')
        
    user_to_manage = get_object_or_404(CustomUser, id=user_id)
    
    if user_to_manage == request.user:
        messages.error(request, "Non puoi bloccare il tuo stesso account!")
        return redirect('manager_users')
        
    user_to_manage.is_active = not user_to_manage.is_active
    user_to_manage.save()
    
    if user_to_manage.is_active:
        messages.success(request, f"Utente '{user_to_manage.username}' RIATTIVATO con successo.")
    else:
        messages.warning(request, f"Utente '{user_to_manage.username}' BLOCCATO. Non potrà più effettuare il login.")
        
    return redirect('manager_users')

@login_required
def update_user_role(request, user_id):
    if not (request.user.is_manager() or request.user.is_superuser):
        messages.error(request, "Accesso negato.")
        return redirect('product_list')
        
    user_to_modify = get_object_or_404(CustomUser, id=user_id)
    
    if user_to_modify == request.user:
        messages.error(request, "Non puoi modificare il tuo stesso ruolo!")
        return redirect('manager_users')
        
    if request.method == 'POST':
        selected_role = request.POST.get('role')
        
        valid_roles = ['customer', 'store_manager']
        
        if selected_role in valid_roles:
            user_to_modify.role = selected_role
            
            if hasattr(user_to_modify, 'is_manager'):
                user_to_modify.is_manager = (selected_role == 'store_manager')
                
            user_to_modify.save()
            
            friendly_role_name = selected_role.replace('_', ' ').title()
            messages.success(request, f"Ruolo di '{user_to_modify.username}' aggiornato in {friendly_role_name}.")
        else:
            messages.error(request, "Ruolo selezionato non valido.")
            
    return redirect('manager_users')