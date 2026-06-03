from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Grazie! La tua recensione è stata pubblicata.")
        else:
            messages.error(request, "Errore durante l'invio della recensione. Controlla i dati.")
            
    return redirect('product_detail', pk=product.id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product_id = review.product.id  
    
    if request.user == review.user or getattr(request.user, 'role', '') == 'store_manager' or request.user.is_superuser:
        
        review.delete()
        messages.success(request, "Recensione eliminata definitivamente dal database.")
    else:
        messages.error(request, "Azione non consentita. Non hai i permessi per eliminare questa recensione.")
        
    return redirect('product_detail', pk=product_id)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product = review.product
    
    if request.user != review.user:
        messages.error(request, "Azione non consentita. Puoi modificare solo le tue recensioni.")
        return redirect('product_detail', pk=product.id)
        
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Recensione aggiornata con successo!")
            return redirect('product_detail', pk=product.id)
        else:
            messages.error(request, "Errore nella compilazione. Controlla i dati inseriti.")
    else:
        form = ReviewForm(instance=review)
        
    return render(request, 'modificaRecensione.html', {
        'form': form,
        'review': review,
        'product': product
    })    