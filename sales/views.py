from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
import re

from .models import Sale
from .forms import SaleForm


@login_required
def sale_list(request):
    search = request.GET.get('search', '')

    sales = Sale.objects.select_related(
        'property', 'customer', 'agent'
    ).order_by('-created_at')
    if getattr(request.user, 'role', '') == 'PROPERTY':
        sales = sales.filter(property__agent=request.user)
    elif not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        sales = sales.filter(agent=request.user)

    if search:
        house_id_match = re.fullmatch(r'LGS-(\d+)', search.strip(), re.IGNORECASE)
        if house_id_match:
            sales = sales.filter(property_id=int(house_id_match.group(1)))
        else:
            sales = sales.filter(
                Q(property__title__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__phone__icontains=search) |
                Q(payment_status__icontains=search)
            )

    return render(request, 'sales/sale_list.html', {
        'sales': sales,
        'search': search,
    })


@login_required
def sale_add(request):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    if request.method == 'POST':
        form = SaleForm(request.POST)

        if form.is_valid():
            sale = form.save(commit=False)
            if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
                sale.agent = request.user
            sale.save()
            messages.success(request, 'Sale added successfully.')
            return redirect('sale_list')
    else:
        form = SaleForm()

    return render(request, 'sales/sale_form.html', {
        'form': form,
        'title': 'Add Sale',
    })


@login_required
def sale_edit(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    sale = get_object_or_404(Sale, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and sale.agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)

        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully.')
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)

    return render(request, 'sales/sale_form.html', {
        'form': form,
        'title': 'Edit Sale',
    })


@login_required
def sale_delete(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    sale = get_object_or_404(Sale, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and sale.agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted successfully.')
        return redirect('sale_list')

    return render(request, 'sales/sale_confirm_delete.html', {
        'sale': sale,
    })
