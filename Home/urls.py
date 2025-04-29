from django.urls import path
from . import views
urlpatterns = [
   # path('test', views.testpage),
    path('', views.Index, name="index"),
    path('shop/', views.Shop, name="shop"),
    path('product_details/<int:id>/', views.Product_details, name="product_details"),
    path('product_cat/<int:id>/', views.Product_cat, name='product_cat'),
    path('product/<int:id>/add-to-cart/', views.Add_to_cart, name='add-to-cart'),    
    path('cart/', views.cart, name='cart'),    
    path('cart/delete', views.Delete_cart, name='delete-cart'),    
    path('cart/create-checkout-session/', views.Create_checkout_session, name='create-checkout-session'),    
    path('cart/checkout_success/', views.Checkout_success, name='checkout_success'),    
    path('product_checkout/<int:id>/', views.Checkout, name='checkout'),


    path('mention_legale/', views.Mention_legale, name="mention_legale"),
]