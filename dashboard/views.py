from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from customers.models import Customer
from properties.models import Property
from sales.models import Sale
from rentals.models import Rental
from accounts.models import User


def home(request):
    return render(request, 'dashboard/home.html')


@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        return agent_dashboard(request)
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': User.objects.count(), 'total_customers': Customer.objects.count(),
        'total_buyers': Customer.objects.filter(customer_type='BUYER').count(),
        'total_renters': Customer.objects.filter(customer_type='RENTER').count(),
        'total_owners': Customer.objects.filter(customer_type__in=['SELLER', 'RENT_OWNER']).count(),
        'available_properties': Property.objects.filter(status='AVAILABLE').count(),
        'sold_properties': Property.objects.filter(status='SOLD').count(),
        'rented_properties': Property.objects.filter(status='RENTED').count(),
        'pending_sales': Sale.objects.filter(payment_status='PENDING').count(),
        'sales_revenue': Sale.objects.filter(payment_status='PAID').aggregate(total=Sum('selling_price'))['total'] or 0,
        'rental_revenue': Rental.objects.filter(status__in=['CONFIRMED', 'ACTIVE', 'COMPLETED']).aggregate(total=Sum('monthly_rent'))['total'] or 0,
        'agent_performance': User.objects.filter(role='AGENT').annotate(customer_count=Count('customers', distinct=True), sale_count=Count('sales', distinct=True), rental_count=Count('rentals', distinct=True)),
    })


@login_required
def agent_dashboard(request):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        return redirect('property_list')

    return render(request, 'dashboard/agent_dashboard.html', {
        'total_customers': Customer.objects.filter(assigned_agent=request.user).count(),
        'total_properties': Property.objects.filter(agent=request.user).count(),
        'total_sales': Sale.objects.filter(agent=request.user).count(),
        'total_rentals': Rental.objects.filter(agent=request.user).count(),
    })
