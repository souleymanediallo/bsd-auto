import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from cars.models import City, SenegalRegion, BodyType


class LandingKind(models.TextChoices):
    STATIC      = "STATIC", "Statique"
    DESTINATION = "DESTINATION", "Destination"
    REGION      = "REGION", "Région"
    CATEGORY    = "CATEGORY", "Catégorie"


class LandingPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    kind = models.CharField(max_length=20, choices=LandingKind.choices, db_index=True)
    title = models.CharField(max_length=170)
    slug = models.SlugField(unique=True, max_length=200, editable=False)

    keyword = models.CharField(max_length=160, blank=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)

    city = models.ForeignKey(
        City, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="DESTINATION uniquement."
    )
    region = models.CharField(
        max_length=20, choices=SenegalRegion.choices, null=True, blank=True,
        help_text="RÉGION uniquement."
    )
    body_type = models.CharField(
        max_length=20, choices=BodyType.choices, null=True, blank=True,
        help_text="CATÉGORIE : ex. SUV, berline, utilitaire…"
    )

    # Contenu / SEO
    content = CKEditor5Field(blank=True, null=True, config_name="default")
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "title"]
        indexes = [
            models.Index(fields=["is_active", "kind"]),
            models.Index(fields=["position"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.slug})"

    # --- Validation conditionnelle
    def clean(self):
        errors = {}
        if self.kind == LandingKind.DESTINATION and not self.city_id:
            errors["city"] = "Obligatoire pour une page Destination."
        if self.kind == LandingKind.REGION and not self.region:
            errors["region"] = "Obligatoire pour une page Région."
        if self.kind == LandingKind.CATEGORY and not self.body_type:
            errors["body_type"] = "Renseignez 'body_type' pour une Catégorie."
        if errors:
            raise ValidationError(errors)

        if not self.meta_title:
            self.meta_title = self.title

    # --- Slug unique (avec suffixe si collision)
    def _build_unique_slug(self, base_text=None):
        base = slugify(base_text or self.title)[:180] or "page"
        candidate = base
        while LandingPage.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base}-{uuid.uuid4().hex[:6]}"
        return candidate

    def save(self, *args, **kwargs):
        # Valider avant
        self.full_clean(exclude=["slug"])

        # Purger les champs non pertinents
        if self.kind == LandingKind.STATIC:
            self.city = None; self.region = None; self.body_type = None
        elif self.kind == LandingKind.DESTINATION:
            self.region = None; self.body_type = None
        elif self.kind == LandingKind.REGION:
            self.city = None; self.body_type = None
        elif self.kind == LandingKind.CATEGORY:
            self.city = None; self.region = None

        # Slug : créer si vide OU régénérer si le titre a changé
        if not self.slug:
            self.slug = self._build_unique_slug()
        else:
            if self.pk:
                old = LandingPage.objects.only("title").get(pk=self.pk)
                if old.title != self.title:
                    self.slug = self._build_unique_slug()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("landing_page", kwargs={"slug": self.slug})
