from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from django.forms import model_to_dict
from django.contrib import messages



User = get_user_model()

def Signup(request):
    if request.method == "POST":
        # traiter le formulaire
        # le nom des clés dans le dictionnaire sont définits par name="" dans la balise html de l'input
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        return redirect('chaima_shop:index')

    return render(request, 'client/signup.html')

def Login_user(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get('password')

        user = authenticate(email = email, password = password)
        if user:
            login(request, user)
            return redirect('chaima_shop:index')

    return render(request, 'client/login.html')

def Logout_user (request):
    logout(request)
    return redirect ('chaima_shop:index')

@login_required
def Profil(request):
    if request.method == "POST":
        # vérifier si le bon mdp est entré
        is_valid = authenticate(email=request.POST.get("email"), password=request.POST.get("password"))
        if is_valid:
            user = request.user
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.save()
        else:
            # on va passer par messages, ils sont associés à la session de l'utilisateur, donc on peut les transporter
            # mais si je boucle sur les messages ils sont supprimés
            # même pas besoin de passer par le context. Une variable dans le html
            messages.add_message(request, messages.ERROR, "les informations ne sont pas corrects.")


    # les valeurs initiales, utiliser model_to_dict() Mais on exclu le champ password
    form = UserForm(initial=model_to_dict(request.user, exclude="password"))
    # récupérer toutes les adresses de l'utilisateur, mettre le shipping en minuscule
    addresses = request.user.addresses.all()

    return render(request, "client/profil.html", context={'form': form,
                                                            "addresses": addresses})
