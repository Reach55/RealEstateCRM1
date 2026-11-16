from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
import re

from .models import Customer
from .forms import CustomerForm, REQUIREMENT_CHOICES
from properties.models import Property
from properties.forms import PHNOM_PENH_DISTRICTS


@login_required
def customer_list(request):
    search = request.GET.get('search', '')
    district = request.GET.get('district', '')
    valid_requirements = {value for value, _label in REQUIREMENT_CHOICES}
    selected_requirements = [
        value for value in request.GET.getlist('requirement')
        if value in valid_requirements
    ]

    customers = Customer.objects.all().order_by('-created_at')
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        customers = customers.filter(assigned_agent=request.user)

    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search) |
            Q(requirements__icontains=search) |
            Q(owner_requirements__icontains=search) |
            Q(preferred_location__icontains=search) |
            Q(preferred_district__icontains=search) |
            Q(district__icontains=search)
        )

    if district:
        customers = customers.filter(
            Q(preferred_location__icontains=district) |
            Q(preferred_district__icontains=district) |
            Q(district__icontains=district)
        )

    if selected_requirements:
        requirement_filter = Q(requirements__icontains=selected_requirements[0]) | Q(
            owner_requirements__icontains=selected_requirements[0]
        )
        for selected_requirement in selected_requirements[1:]:
            requirement_filter |= (
                Q(requirements__icontains=selected_requirement) |
                Q(owner_requirements__icontains=selected_requirement)
            )
        customers = customers.filter(requirement_filter)

    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'search': search,
        'district': district,
        'selected_requirements': selected_requirements,
        'district_choices': PHNOM_PENH_DISTRICTS,
        'requirement_choices': REQUIREMENT_CHOICES,
    })


@login_required
def customer_detail(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    customer = get_object_or_404(Customer, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and customer.assigned_agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if customer.customer_type not in ('BUYER', 'RENTER'):
        properties = Property.objects.none()
    else:
        properties = Property.objects.filter(status='AVAILABLE')
        properties = properties.filter(listing_type='RENT' if customer.customer_type == 'RENTER' else 'SALE')
    if customer.property_type:
        properties = properties.filter(property_type=customer.property_type)
    preferred_district = customer.preferred_location or customer.preferred_district
    if preferred_district:
        properties = properties.filter(
            Q(district__icontains=preferred_district) |
            Q(location__icontains=preferred_district)
        )
    price_field = 'monthly_rent' if customer.customer_type == 'RENTER' else 'price'
    if customer.minimum_budget:
        properties = properties.filter(**{f'{price_field}__gte': customer.minimum_budget})
    if customer.budget:
        properties = properties.filter(**{f'{price_field}__lte': customer.budget})
    if customer.preferred_bedrooms:
        properties = properties.filter(bedrooms__gte=customer.preferred_bedrooms)
    if customer.preferred_bathrooms:
        properties = properties.filter(bathrooms__gte=customer.preferred_bathrooms)
    return render(request, 'customers/customer_detail.html', {'customer': customer, 'properties': properties[:12]})


@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
                customer.assigned_agent = request.user
            customer.save()
            messages.success(request, 'Customer added successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm()

    return render(request, 'customers/customer_form.html', {
        'form': form,
        'title': 'Add Customer',
    })


@login_required
def customer_edit(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    customer = get_object_or_404(Customer, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and customer.assigned_agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/customer_form.html', {
        'form': form,
        'title': 'Edit Customer',
    })


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and customer.assigned_agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {
        'customer': customer,
    })


@login_required
def customer_matches(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    customer = get_object_or_404(Customer, pk=pk)

    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and customer.assigned_agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    properties = Property.objects.filter(status='AVAILABLE')
    if customer.customer_type == 'BUYER':
        properties = properties.filter(listing_type='SALE')
    elif customer.customer_type == 'RENTER':
        properties = properties.filter(listing_type='RENT')
    else:
        properties = properties.none()
    if customer.property_type:
        properties = properties.filter(property_type=customer.property_type)

    rent_customer = customer.customer_type == 'RENTER'
    price_field = 'monthly_rent' if rent_customer else 'price'
    if customer.minimum_budget:
        properties = properties.filter(**{f'{price_field}__gte': customer.minimum_budget})
    if customer.budget:
        properties = properties.filter(**{f'{price_field}__lte': customer.budget})

    preferred_district = customer.preferred_location or customer.preferred_district
    if preferred_district:
        properties = properties.filter(
            Q(district__icontains=preferred_district) |
            Q(location__icontains=preferred_district)
        )
    if customer.preferred_commune:
        properties = properties.filter(commune__icontains=customer.preferred_commune)

    if customer.preferred_bedrooms:
        properties = properties.filter(
            bedrooms__gte=customer.preferred_bedrooms
        )

    if customer.preferred_bathrooms:
        properties = properties.filter(
            bathrooms__gte=customer.preferred_bathrooms
        )

    requirements = (customer.requirements or '').lower()
    requirements = re.sub(r'\bswimmingpool\b', 'swimming pool', requirements)
    requirements = re.sub(r'\bpool\b', 'swimming pool', requirements)
    requirements = re.sub(r'\bcar parking\b', 'parking', requirements)

    feature_keywords = {
        'swimming pool': 'swimming_pool',
        'parking': 'parking',
        'garden': 'garden',
        'furnished': 'furnished',
        'fully furnished': 'furnished',
        'gym': 'gym',
        'elevator': 'elevator',
        'security': 'security',
        'balcony': 'balcony',
        'air conditioning': 'air conditioning',
        'pet friendly': 'pet friendly',
    }

    requested_features = []

    for keyword, field in feature_keywords.items():
        if keyword in requirements:
            requested_features.append(field)
            if field in ('swimming_pool', 'parking', 'garden', 'furnished'):
                properties = properties.filter(**{field: True})
            else:
                properties = properties.filter(features__icontains=field)

    for keyword in feature_keywords:
        requirements = requirements.replace(keyword, '')

    stop_words = [
        'need', 'want', 'with', 'house', 'villa',
        'a', 'an', 'the', 'and', 'or', 'have',
        'has', 'looking for'
    ]

    for word in stop_words:
        requirements = re.sub(
            r'\b' + re.escape(word) + r'\b',
            '',
            requirements
        )

    other_keywords = [
        word.strip()
        for word in re.split(r'[,;]', requirements)
        if len(word.strip()) > 2
    ]

    for keyword in other_keywords:
        properties = properties.filter(
            Q(features__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword)
        )

    return render(request, 'customers/customer_matches.html', {
        'customer': customer,
        'properties': properties,
        'requested_features': requested_features,
    })
