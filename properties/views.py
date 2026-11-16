
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from .models import Property, PropertyPhoto
from .forms import PHNOM_PENH_DISTRICTS, PropertyForm
from django.contrib.auth import get_user_model


@login_required
def property_list(request):

    properties = Property.objects.all().order_by('-created_at')
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        properties = properties.filter(agent=request.user)

    filters = {
        'listing_type': request.GET.get('listing_type', ''),
        'status': request.GET.get('status', ''),
        'property_type': request.GET.get('property_type', ''),
        'district': request.GET.get('district', ''),
        'bedrooms': request.GET.get('bedrooms', ''),
        'bathrooms': request.GET.get('bathrooms', ''),
        'min_price': request.GET.get('min_price', ''),
        'max_price': request.GET.get('max_price', ''),
        'min_area': request.GET.get('min_area', ''),
        'max_area': request.GET.get('max_area', ''),
        'property_id': request.GET.get('property_id', ''),
        'keyword': request.GET.get('keyword', ''),
        'swimming_pool': request.GET.get('swimming_pool', ''),
        'parking': request.GET.get('parking', ''),
        'garden': request.GET.get('garden', ''),
        'furnished': request.GET.get('furnished', ''),
    }

    if filters['listing_type']:
        properties = properties.filter(
            listing_type=filters['listing_type']
        )
    if filters['status']:
        properties = properties.filter(status=filters['status'])

    if filters['property_type']:
        properties = properties.filter(
            property_type=filters['property_type']
        )

    if filters['district']:
        properties = properties.filter(
            Q(district__icontains=filters['district']) |
            Q(location__icontains=filters['district'])
        )

    if filters['bedrooms']:
        properties = properties.filter(
            bedrooms=filters['bedrooms']
        )

    if filters['bathrooms']:
        properties = properties.filter(
            bathrooms=filters['bathrooms']
        )

    if filters['min_price']:
        properties = properties.filter(
            price__gte=filters['min_price']
        )

    if filters['max_price']:
        properties = properties.filter(
            price__lte=filters['max_price']
        )

    if filters['min_area']:
        properties = properties.filter(
            area__gte=filters['min_area']
        )

    if filters['max_area']:
        properties = properties.filter(
            area__lte=filters['max_area']
        )

    property_id = filters['property_id'].strip().upper()
    if property_id.startswith('LGS-'):
        property_id = property_id[4:]
    if property_id:
        if property_id.isdigit():
            properties = properties.filter(id=int(property_id))
        else:
            properties = properties.none()

    if filters['keyword']:
        properties = properties.filter(
            Q(title__icontains=filters['keyword']) |
            Q(description__icontains=filters['keyword']) |
            Q(features__icontains=filters['keyword']) |
            Q(location__icontains=filters['keyword'])
        )

    for feature in [
        'swimming_pool',
        'parking',
        'garden',
        'furnished'
    ]:
        if filters[feature] == '1':
            properties = properties.filter(**{feature: True})

    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'filters': filters,
        'property_types': Property.PROPERTY_TYPES,
        'districts': PHNOM_PENH_DISTRICTS,
    })


@login_required
def property_add(request):

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
                obj.agent = request.user
            obj.save()
            for photo in request.FILES.getlist('photos'):
                PropertyPhoto.objects.create(property=obj, image=photo)
            messages.success(request, f'Property added successfully. House ID: {obj.house_id}')
            return redirect('property_list')

    else:
        form = PropertyForm()

    return render(request, 'properties/property_form.html', {
        'form': form
    })


@login_required
def property_edit(request, pk):

    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    property_obj = get_object_or_404(Property, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and property_obj.agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        form = PropertyForm(
            request.POST,
            request.FILES,
            instance=property_obj
        )

        if form.is_valid():
            form.save()
            for photo in request.FILES.getlist('photos'):
                PropertyPhoto.objects.create(property=property_obj, image=photo)
            messages.success(request, 'Property updated successfully.')
            return redirect('property_list')

    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'properties/property_form.html', {
        'form': form
    })


@login_required
def property_delete(request, pk):

    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    property_obj = get_object_or_404(Property, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and property_obj.agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('property_list')

    return render(request, 'properties/property_confirm_delete.html', {
        'property': property_obj
    })


@login_required
def property_interested_customers(request, pk):
    if getattr(request.user, 'role', '') == 'PROPERTY':
        raise PermissionDenied

    from customers.models import Customer
    from django.db.models import Q
    property_obj = get_object_or_404(Property, pk=pk)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN') and property_obj.agent_id != request.user.id:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    customers = Customer.objects.filter(customer_type__in=['BUYER', 'SELLER', 'RENTER', 'RENT_OWNER'])
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'ADMIN'):
        customers = customers.filter(assigned_agent=request.user)
    if property_obj.property_type:
        customers = customers.filter(Q(property_type='') | Q(property_type=property_obj.property_type))
    customers = customers.filter(Q(preferred_location='') | Q(preferred_location__icontains=property_obj.location) | Q(preferred_city='') | Q(preferred_city__icontains=property_obj.city))
    ceiling = property_obj.monthly_rent if property_obj.listing_type == 'RENT' else property_obj.price
    customers = customers.filter(Q(budget=0) | Q(budget__gte=ceiling))
    return render(request, 'properties/interested_customers.html', {'property': property_obj, 'customers': customers.distinct()})
