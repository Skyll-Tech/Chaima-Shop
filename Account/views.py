from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from django.forms import model_to_dict
from django.contrib import messages



User = get_user_model()

def Signup(request):
    errors = []  # liste qui contiendra les messages d'erreur
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Vérifier que l'email et le mot de passe sont bien fournis
        if not email:
            errors.append("L'adresse email est requise.")
        if not password:
            errors.append("Le mot de passe est requis.")
        
        # Vérifier que l'email n'est pas déjà utilisé
        if email and User.objects.filter(email=email).exists():
            errors.append("Cette adresse email est déjà utilisée.")
        
        # Si des erreurs sont détectées, les afficher dans le template
        if errors:
            return render(request, 'client/signup.html', {'errors': errors})
        
        # Tenter de créer l'utilisateur dans un bloc try/except
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
        except Exception as e:
            errors.append("Une erreur s'est produite lors de la création de l'utilisateur : " + str(e))
            return render(request, 'client/signup.html', {'errors': errors})
        
        # Connecter l'utilisateur et rediriger vers la page d'accueil
        login(request, user)
        return redirect('chaima_shop:index')

    return render(request, 'client/signup.html')

def Login_user(request):
    errors = []  # Liste des messages d'erreur
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not email:
            errors.append("L'adresse email est obligatoire.")
        if not password:
            errors.append("Le mot de passe est obligatoire.")
        
        if not errors:
            user = authenticate(request, email=email, password=password)
            
            # En cas de modèle utilisateur par défaut, utilisez : user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('chaima_shop:index')
            else:
                errors.append("Email et/ou mot de passe incorrect.")
    
    # On affiche toujours le formulaire, avec éventuellement des erreurs
    return render(request, 'client/login.html', {'errors': errors})

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
