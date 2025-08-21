# apps/cars/forms.py
import datetime

from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Car, CarPhoto, Place, CarFeature

MAX_PHOTOS = 6
class CarForm(forms.ModelForm):
    place = forms.ModelChoiceField(
        queryset=Place.objects.select_related("city").order_by("city__name"),
        label="Lieu",
        widget=forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Lieu"}),
        required=True,
    )
    features = forms.ModelMultipleChoiceField(
        queryset=CarFeature.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="Options disponibles",
    )
    class Meta:
        model = Car
        fields = (
            "title", "brand", "year", "mileage_km",
            "body_type", "transmission", "fuel_type",
            "seats", "doors", "color", "place",
            "description", "features", "daily_price", "is_active"
        )
        widgets = {
            "title":       forms.TextInput(attrs={"class": "form-control"}),
            "year":        forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Année"}),
            "mileage_km":  forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Kilométrage"}),
            "brand":       forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Marque"}),
            "body_type":   forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Carrosserie"}),
            "transmission":forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Boîte"}),
            "fuel_type":   forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Carburant"}),
            "seats":       forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Places"}),
            "doors":       forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Portes"}),
            "color":       forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Couleur"}),
            "place":       forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Lieu"}),
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "daily_price": forms.Select(attrs={"class": "form-select", "data-select": "", "aria-label": "Prix / jour"}),
            "is_active":   forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remplir les années de 2010 à l’année actuelle + 1
        self.fields["features"].queryset = CarFeature.objects.all().order_by("name")
        # place = self.fields.get("place")
        def label_place(p: Place):
            region_label = p.get_region_display() if hasattr(p, "get_region_display") else p.region
            return f"{p.city.name}, {region_label}"
        self.fields["place"].label_from_instance = label_place


class CarPhotoForm(forms.ModelForm):
    class Meta:
        model = CarPhoto
        fields = ["image", "caption", "is_cover", "order"]
        widgets = {
            "image":   forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "caption": forms.HiddenInput(),
            "is_cover":forms.HiddenInput(),
            "order":   forms.HiddenInput(),
        }


class BaseCarPhotoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total, covers = 0, 0
        for form in self.forms:
            if getattr(form, "cleaned_data", None) and not form.cleaned_data.get("DELETE"):
                if form.cleaned_data.get("image") or form.instance.pk:
                    total += 1
                    if form.cleaned_data.get("is_cover"):
                        covers += 1
        if total == 0:
            from django.core.exceptions import ValidationError
            raise ValidationError("Ajoutez au moins une photo.")
        if covers == 0 and total > 0:
            # forcer la première en cover après save (voir vue)
            pass

CarPhotoFormSet = inlineformset_factory(
    Car, CarPhoto,
    form=CarPhotoForm,
    formset=BaseCarPhotoFormSet,
    fields=["image", "caption", "is_cover", "order"],
    extra=3, max_num=6, validate_max=True, can_delete=True
)


class EditCarPhotoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        covers = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            # Compte l'existant si pas de nouvel upload
            has_existing = bool(getattr(form.instance, "pk", None) and getattr(form.instance, "image", None))
            has_new = bool(form.cleaned_data.get("image"))

            if has_existing or has_new:
                total += 1

            # Couvre aussi le cas où la case n'a pas bougé (on reprend la valeur instance)
            is_cover = form.cleaned_data.get("is_cover")
            if is_cover is None:
                is_cover = getattr(form.instance, "is_cover", False)
            if is_cover:
                covers += 1

            # ordre >= 0 si saisi
            order = form.cleaned_data.get("order")
            if order is not None and order < 0:
                form.add_error("order", "L’ordre doit être ≥ 0.")

        if total == 0:
            # En édition on autorise 0 seulement si l’utilisateur n’a pas supprimé celles qui existaient
            # mais comme on vient de compter l'existant, 0 signifie vraiment "aucune"
            raise ValidationError("Ajoutez au moins une photo.")

        if covers > 1:
            raise ValidationError("Sélectionnez une seule photo de couverture.")

EditCarPhotoFormSet = inlineformset_factory(
    Car,
    CarPhoto,
    fields=["image", "caption", "is_cover", "order"],
    extra=0,
    can_delete=True,
    formset=EditCarPhotoFormSet,
)