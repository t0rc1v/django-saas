from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterForm

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            login(request, User)

            messages.success(request, "Account successfully created!")    

            # return redirect("course_list")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form}) 

def login_user(request):
    if request.method == 'POST':
  
        # AuthenticationForm_can_also_be_used__
  
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {username} !!')
        else:
            messages.info(request, "Please enter a correct username and password. Note that both fields may be case-sensitive.")

    return render(request, 'users/login.html')