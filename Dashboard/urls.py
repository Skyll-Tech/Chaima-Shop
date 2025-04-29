from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static
urlpatterns = [
    path('dashboard/', views.Dashboard, name='dashboard'),

    path('show_categories/', views.Show_categories, name='show_categories'),
    path('create_categorie/', views.Create_categorie, name= 'create_categorie'),
    path('update_categorie/<int:id>/', views.Update_categorie, name='update_categorie'),
    path('delete_categorie/<int:id>/', views.Delete_categorie, name='delete_categorie'),

    path('create_product/', views.Create_product, name='create_product'),
    path('show_product/', views.Show_product, name = 'show_product'),
    path('update_product/<int:id>/', views.Update_product, name='update_product'),
    path('delete_product/<int:id>/', views.Delete_product, name='delete_product'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
