from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

from .choices_types import (
    SenegalRegion, Transmission, FuelType, BodyType, CarColor, COLOR_HEX_BY_VALUE
)

import os, uuid

User = settings.AUTH_USER_MODEL

PRICE_CHOICES = [(p, f"{p:,} F".replace(",", " ")) for p in range(15000, 100001, 5000)]
MILEAGE_CHOICES = [(p, f"{p:,} km".replace(",", " ")) for p in range(10000, 300001, 5000)]

# Create your models here.
def current_year_plus_one():
    return timezone.now().year + 1

def car_photo_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"cars/{instance.car_id}/photos/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}"


class City(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    slug = models.SlugField(max_length=80, unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"
        ordering = ["name"]


class Place(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="places", verbose_name="Ville")
    region = models.CharField(max_length=20, choices=SenegalRegion.choices)
    country = models.CharField(max_length=2, default="SN", editable=False, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    validators=[MinValueValidator(-180), MaxValueValidator(180)])

    class Meta:
        verbose_name = "Lieu"
        verbose_name_plural = "Lieux"
        indexes = [
            models.Index(fields=["city", "region"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.city}, {self.region} (SN)"

    def save(self, *args, **kwargs):
        # Sécurité : on force le pays à 'SN' quoi qu’il arrive.
        self.country = "SN"
        super().save(*args, **kwargs)

    @property
    def country_name(self):
        return "Sénégal"


class Brand(models.Model):
    name = models.CharField(max_length=60, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["brand__name", "name"]
        constraints = [models.UniqueConstraint(fields=["brand", "name"], name="uniq_brand_model")]

    def __str__(self):
        return f"{self.brand} {self.name}"


class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars", verbose_name="Propriétaire")
    title = models.CharField(max_length=140, help_text="Titre de l’annonce (ex: Toyota Yaris 2020 propre)")
    slug = models.SlugField(max_length=160, unique=True, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="cars", verbose_name="cars_brand")
    model_name = models.ForeignKey(CarModel, on_delete=models.PROTECT, related_name="cars_models", verbose_name="Modèle")
    year = models.PositiveIntegerField(validators=[MinValueValidator(2010), MaxValueValidator(current_year_plus_one)])
    body_type = models.CharField(max_length=12, choices=BodyType.choices, default=BodyType.CITY_CAR)
    transmission = models.CharField(max_length=10, choices=Transmission.choices, default=Transmission.MANUAL)
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices, default=FuelType.GASOLINE)
    seats = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(20)])
    doors = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(2), MaxValueValidator(4)])
    mileage_km = models.PositiveIntegerField(choices=MILEAGE_CHOICES, default=10000)
    color = models.CharField(max_length=10, choices=CarColor.choices, default=CarColor.WHITE)
    description = models.TextField(blank=True)
    features = models.ManyToManyField("CarFeature", blank=True, related_name="cars")
    place = models.ForeignKey(Place, on_delete=models.PROTECT, related_name="cars")
    daily_price = models.PositiveIntegerField(choices=PRICE_CHOICES, default=15000)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    class Meta:
        verbose_name = "Voiture"
        verbose_name_plural = "Voitures"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "place"]),
            models.Index(fields=["brand", "model_name", "year"]),
            models.Index(fields=["daily_price"]),
            models.Index(fields=["place", "daily_price"]),
        ]

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.year} — {self.owner}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.brand}-{self.model_name}-{self.year}")
            base = base[:150]
            self.slug = f"{base}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    @property
    def cover_photo(self):
        return self.photos.filter(is_cover=True).first()

    @property
    def color_hex(self) -> str:
        return COLOR_HEX_BY_VALUE.get(self.color, COLOR_HEX_BY_VALUE.get("other", "#9e9e9e"))

    def get_absolute_url(self):
        return reverse("car_detail", args=[self.pk])

    def clean(self):
        super().clean()
        if self.model_name and self.brand and self.model_name.brand_id != self.brand_id:
            raise ValidationError({"model_name": "Ce modèle n’appartient pas à la marque sélectionnée."})


class CarFeature(models.Model):
    name = models.CharField(max_length=180, unique=True)
    icon = models.CharField(max_length=180, blank=True)
    slug = models.SlugField(max_length=180, unique=True, editable=False)

    class Meta:
        verbose_name = "Caractéristique"
        verbose_name_plural = "Caractéristiques"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CarPhoto(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=car_photo_upload_to)
    caption = models.CharField(max_length=140, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo de voiture"
        verbose_name_plural = "Photos de voiture"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["car"], condition=models.Q(is_cover=True),
                                    name="unique_cover_per_car")
        ]

    def __str__(self):
        return f"Photo #{self.pk} — {self.car}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_cover:
            CarPhoto.objects.filter(car=self.car).exclude(pk=self.pk).update(is_cover=False)