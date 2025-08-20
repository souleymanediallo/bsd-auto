# pages/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import NoReverseMatch

from .models import LandingPage, LandingKind


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    # Liste
    list_display = (
        "title",
        "kind",
        "target_display",   # ville / région / catégorie
        "position",
        "is_active",
        "public_link",      # lien cliquable vers la page publique
        "updated_at",
    )
    list_display_links = ("title",)
    list_editable = ("position", "is_active")
    list_filter = ("kind", "is_active", "region", "body_type")
    search_fields = ("title", "slug", "keyword", "meta_title", "meta_description", "content")
    ordering = ("position", "title")

    # Formulaire
    readonly_fields = ("slug", "created_at", "updated_at")
    autocomplete_fields = ["city"]

    fieldsets = (
        ("Informations", {
            "fields": ("kind", "title", "slug", "keyword", "position", "is_active"),
        }),
        ("Cibles (selon le type)", {
            "fields": ("city", "region", "body_type"),
            "classes": ("collapse",),
            "description": "Renseigner uniquement le champ pertinent selon le type : "
                           "Destination → ville, Région → région, Catégorie → type de carrosserie.",
        }),
        ("Contenu", {
            "fields": ("content",),
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
        }),
        ("Dates", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("city")

    @admin.display(description="URL")
    def public_link(self, obj: LandingPage):
        """Affiche un lien cliquable vers l’URL publique."""
        try:
            url = obj.get_absolute_url()  # doit fonctionner si ton urls.py expose pages:landing_page
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        except NoReverseMatch:
            return "—"

    @admin.display(description="Cible", ordering="city__name")
    def target_display(self, obj: LandingPage):
        """Affiche la cible humaine selon le type de page."""
        if obj.kind == LandingKind.DESTINATION and obj.city:
            return obj.city.name
        if obj.kind == LandingKind.REGION and obj.region:
            return obj.get_region_display()
        if obj.kind == LandingKind.CATEGORY and obj.body_type:
            return obj.get_body_type_display()
        return "—"
