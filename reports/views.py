from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from customers.models import Customer
from properties.models import Property
from rentals.models import Rental
from sales.models import Sale


@login_required
def agent_report(request):
    is_admin = request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'

    if getattr(request.user, 'role', '') == 'PROPERTY':
        houses = Property.objects.filter(agent=request.user).order_by('-created_at')
        return render(request, 'reports/property_report.html', {
            'title': 'My Property Additions',
            'houses': houses,
        })

    customers = Customer.objects.all()
    properties = Property.objects.all()
    sales = Sale.objects.all()
    rentals = Rental.objects.all()

    if not is_admin:
        customers = customers.filter(assigned_agent=request.user)
        properties = properties.filter(agent=request.user)
        sales = sales.filter(agent=request.user)
        rentals = rentals.filter(agent=request.user)

    active_rentals = rentals.filter(status__in=['CONFIRMED', 'ACTIVE'])
    paid_sales = sales.filter(payment_status='PAID')

    return render(request, 'reports/agent_report.html', {
        'is_admin': is_admin,
        'title': 'Agency Report' if is_admin else 'My Reports',
        'total_customers': customers.count(),
        'total_properties': properties.count(),
        'total_sales': sales.count(),
        'paid_sales_revenue': paid_sales.aggregate(total=Sum('selling_price'))['total'] or 0,
        'total_rentals': rentals.count(),
        'active_rental_value': active_rentals.aggregate(total=Sum('monthly_rent'))['total'] or 0,
    })
