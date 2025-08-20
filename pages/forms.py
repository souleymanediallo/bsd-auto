from django import forms
from cars.models import BodyType, SenegalRegion


class CarSearchForm(forms.Form):
    body_type = forms.ChoiceField(
        label="Catégorie",
        required=False,
        choices=[("", "Catégorie de voiture")] + list(BodyType.choices),
        widget=forms.Select(attrs={
            "class": "form-select form-select-xl",
            "data-select": '{"searchEnabled": true}',
            "aria-label": "Catégorie de voiture",
            "data-bs-theme": "light",
        }),
    )
    region = forms.ChoiceField(
        label="Région",
        required=False,
        choices=[("", "Région")] + list(SenegalRegion.choices),
        widget=forms.Select(attrs={
            "class": "form-select form-select-xl",
            "data-select": '{"searchEnabled": true}',
            "aria-label": "Région",
            "data-bs-theme": "light",
        }),
    )