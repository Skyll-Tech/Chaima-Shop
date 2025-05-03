from django.urls import path
from . import views
urlpatterns = [
   # path('test', views.testpage),
    path('signup', views.Signup, name="signup"),
    path('login', views.Login_user, name="login"),
    path('logout', views.Logout_user, name="logout"),
    path('profil', views.Profil, name="profil"),
]