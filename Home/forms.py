from django import forms
from store.models import Order


class OrderForm(forms.ModelForm):
    # je modifie le widget utilisé
    quantity = forms.ChoiceField(choices=[(i, i) for i in range(1, 11)])
    # relier le delete à save que l'on surcharge
    delete = forms.BooleanField(initial=False, required=False, label="Supprimer")

    class Meta:
        model = Order
        # uniquement le champ de la quantité
        fields = ["quantity"]

    def save(self, *args, **kwargs):
        if self.cleaned_data["delete"]:
            # j"utilise return pour arrêter la fonction save car sinon on va supprimer puis sauvegarder l'instance
            self.instance.delete()
            # je veux supprimer le panier si je n'ai plus d'articles dedans
            # instance(Order).utilisateur.panier.articles
            # pour savoir combien d'éléments contient un queryset .count()
            if self.instance.user.cart.orders.count() == 0:
                self.instance.user.cart.delete()
                # retourne True pour dire que bien supprimer et ne pas aller dans le save
                return True
        return super().save(*args, **kwargs)
