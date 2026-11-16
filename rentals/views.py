from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from .models import Rental
from .forms import RentalForm

@login_required
def rental_list(request):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    rentals = Rental.objects.select_related('tenant', 'property', 'agent').order_by('-created_at')
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        rentals = rentals.filter(agent=request.user)
    return render(request, 'rentals/rental_list.html', {'rentals': rentals})

@login_required
def rental_add(request):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    form = RentalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rental = form.save(commit=False)
        if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
            rental.agent = request.user
        rental.save()
        messages.success(request, 'Rental saved.')
        return redirect('rental_list')
    return render(request, 'rentals/rental_form.html', {'form': form})
