from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    City, Place, Brand, CarModel,
    Car, CarFeature, CarPhoto
)

# ---------- Utilitaires d’affichage ----------
def format_price(amount: int) -> str:
    return f"{amount:,} F".replace(",", " ")


# ---------- City ----------
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("slug",)


# ---------- Place ----------
@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("city", "region", "country")
    list_filter = ("region", "country")
    search_fields = ("city__name",)
    autocomplete_fields = ("city",)
    readonly_fields = ("country_name",)


# ---------- Brand ----------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


# ---------- CarModel ----------
@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand")
    list_filter = ("brand",)
    search_fields = ("name", "brand__name")
    autocomplete_fields = ("brand",)
    ordering = ("brand__name", "name")


# ---------- Inlines Photos ----------
class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 1
    fields = ("preview", "image", "caption", "is_cover", "order", "uploaded_at")
    readonly_fields = ("preview", "uploaded_at")

    @admin.display(description="Aperçu")
    def preview(self, obj: CarPhoto):
        if obj.id and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:90px;object-fit:cover;border-radius:6px;border:1px solid #ddd;" />',
                obj.image.url
            )
        return "—"


# ---------- Car ----------
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "title", "brand", "model_name", "year",
        "color_badge", "price_display",
        "owner", "place", "is_active", "is_featured", "created_at",
    )
    list_filter = (
        "is_active", "is_featured",
        "brand", "model_name",
        "body_type", "transmission", "fuel_type",
        "color", "year", "place__region",
    )
    search_fields = (
        "title", "brand__name", "model_name__name",
        "owner__username", "owner__email",
        "place__city__name",
    )
    autocomplete_fields = ("brand", "model_name", "owner", "place")
    filter_horizontal = ("features",)
    readonly_fields = ("slug", "created_at", "updated_at", "cover_preview")
    inlines = [CarPhotoInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        ("Informations principales", {
            "fields": ("owner", "title", "slug", "brand", "model_name", "year", "body_type")
        }),
        ("Caractéristiques", {
            "fields": ("transmission", "fuel_type", "seats", "doors", "mileage_km", "color", "features")
        }),
        ("Localisation & Prix", {
            "fields": ("place", "daily_price")
        }),
        ("Médias", {
            "fields": ("cover_preview",),
            "description": "Ajoutez les photos dans l’onglet ci-dessous (inlines)."
        }),
        ("Statut", {
            "fields": ("is_active", "is_featured", "created_at", "updated_at")
        }),
    )

    # --------- Affichages custom ---------
    @admin.display(description="Couleur")
    def color_badge(self, obj: Car):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:.4rem">'
            '<span style="width:14px;height:14px;border-radius:50%;display:inline-block;'
            'border:1px solid rgba(0,0,0,.2);background:{}"></span>{}'
            "</span>",
            obj.color_hex,
            obj.get_color_display()
        )

    @admin.display(description="Prix / jour", ordering="daily_price")
    def price_display(self, obj: Car):
        return format_price(obj.daily_price)

    @admin.display(description="Cover")
    def cover_preview(self, obj: Car):
        photo = obj.cover_photo
        if photo and photo.image:
            return format_html(
                '<img src="{}" style="height:100px;width:160px;object-fit:cover;border-radius:8px;border:1px solid #ddd;" />',
                photo.image.url
            )
        return mark_safe('<span style="opacity:.6">Aucune photo de couverture</span>')

    # --------- Actions utiles ---------
    actions = ["activer", "desactiver", "mettre_en_avant", "retirer_mise_en_avant"]

    @admin.action(description="Activer les annonces sélectionnées")
    def activer(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} annonce(s) activée(s).")

    @admin.action(description="Désactiver les annonces sélectionnées")
    def desactiver(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} annonce(s) désactivée(s).")

    @admin.action(description="Mettre en avant")
    def mettre_en_avant(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} annonce(s) mises en avant.")

    @admin.action(description="Retirer la mise en avant")
    def retirer_mise_en_avant(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} annonce(s) retirées de la mise en avant.")


# ---------- CarFeature ----------
@admin.register(CarFeature)
class CarFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "slug")
    search_fields = ("name", "slug", "icon")
    ordering = ("name",)
    readonly_fields = ("slug",)


# ---------- CarPhoto (si tu veux aussi l’éditer hors inline) ----------
@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
    list_display = ("car", "is_cover", "order", "uploaded_at", "thumb")
    list_filter = ("is_cover", "uploaded_at", "car__brand")
    search_fields = ("car__title", "car__brand__name", "car__model_name__name")
    autocomplete_fields = ("car",)

    @admin.display(description="Aperçu")
    def thumb(self, obj: CarPhoto):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;width:75px;object-fit:cover;border-radius:6px;border:1px solid #ddd;" />',
                obj.image.url
            )
        return "—"
