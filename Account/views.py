from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate

User = get_user_model()

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect ('index')

    return render(request, 'client/signup.html')

def Login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect('index')

    return render(request, 'client/login.html')

def Logout_user (request):
    logout(request)
    return redirect ('index')
