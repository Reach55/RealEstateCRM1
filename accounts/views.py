from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .forms import UserForm

User = get_user_model()

def login_view(request):

    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        if request.user.role == 'PROPERTY':
            return redirect('property_list')
        return redirect('agent_dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            if user.role == 'PROPERTY':
                return redirect('property_list')
            else:
                return redirect('agent_dashboard')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


@login_required
def home_view(request):
    return render(request, 'accounts/home.html')


def logout_view(request):
    logout(request)
    return redirect('login')

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')

    search = request.GET.get('search', '')
    if search:
        users = users.filter(username__icontains=search)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'search': search,
    })


@login_required
@user_passes_test(is_admin)
def user_add(request):
    form = UserForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('user_list')

    return render(request, 'accounts/user_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')

    return render(request, 'accounts/user_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')

    return render(request, 'accounts/user_confirm_delete.html', {'user': user})
