import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Count, Prefetch


logger = logging.getLogger(__name__)

from .models import Car, Favorite, CarPhoto
from .forms import CarForm, CarPhotoFormSet, EditCarPhotoFormSet

FORMSET_PREFIX = "photos"
PHOTO_PREFIX = "photos"

def _ensure_one_cover(car):
    qs = car.photos.order_by("order", "id")
    if not qs.filter(is_cover=True).exists():
        first = qs.first()
        if first:
            first.is_cover = True
            first.save(update_fields=["is_cover"])


@login_required
@transaction.atomic
def car_create(request):
    car_form = CarForm(request.POST or None)
    photo_formset = CarPhotoFormSet(request.POST or None, request.FILES or None, prefix="photos")

    if request.method == "POST":
        valid = car_form.is_valid() and photo_formset.is_valid()
        if valid:
            car = car_form.save(commit=False)
            car.owner = request.user
            car.save()
            car_form.save_m2m()

            photo_formset.instance = car
            photo_formset.save()
            _ensure_one_cover(car)

            return redirect(car.get_absolute_url())
        else:
            logger.error("car_form errors: %s", car_form.errors.as_json())
            logger.error("photo_formset non_form_errors: %s", photo_formset.non_form_errors())
            for i, f in enumerate(photo_formset.forms):
                logger.error("photo_formset[%s] errors: %s", i, f.errors.as_json())

    return render(request, "cars/car_form.html", {
        "car_form": car_form,
        "photo_formset": photo_formset,
    })


@login_required
@transaction.atomic
def car_update(request, slug):
    car = get_object_or_404(Car, slug=slug)

    # Seul le propriétaire (ou un staff) peut modifier
    if request.user != car.owner and not request.user.is_staff:
        messages.warning(request, "Vous n'avez pas la permission de modifier cette annonce.")
        return redirect("cars_list")

    car_form = CarForm(request.POST or None, instance=car)
    photo_formset = CarPhotoFormSet(
        request.POST or None, request.FILES or None,
        instance=car, prefix="photos"
    )

    if request.method == "POST":
        valid = car_form.is_valid() and photo_formset.is_valid()
        if valid:
            car = car_form.save()
            photo_formset.save()
            _ensure_one_cover(car)
            messages.success(request, "Annonce mise à jour avec succès.")
            return redirect(car.get_absolute_url())
        else:
            logger.error("car_form errors: %s", car_form.errors.as_json())
            logger.error("photo_formset non_form_errors: %s", photo_formset.non_form_errors())
            for i, f in enumerate(photo_formset.forms):
                logger.error("photo_formset[%s] errors: %s", i, f.errors.as_json())

    return render(request, "cars/car_form.html", {
        "car_form": car_form,
        "photo_formset": photo_formset,
        "is_update": True,   # utile pour adapter le template (titre/bouton)
        "car": car,
    })



@login_required
@require_http_methods(["GET", "POST"])
def car_delete(request, slug):
    car = get_object_or_404(Car, slug=slug)

    if car.owner_id != request.user.id:
        raise PermissionDenied("Vous ne pouvez pas supprimer cette annonce.")

    if request.method == "POST":
        title = str(car)
        car.delete()
        messages.success(request, f"L’annonce « {title} » a été supprimée.")
        return redirect("cars_list")

    # GET -> page de confirmation
    return render(request, "cars/car_confirm_delete.html", {"car": car})

class CarListView(ListView):
    model = Car
    template_name = "cars/car_list.html"      # le template ci-dessous
    context_object_name = "cars"
    paginate_by = 12                      # ⇦ mets 4 si tu veux seulement 4 cartes
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (Car.objects
              .filter(is_active=True)
              .select_related("brand", "model_name", "place__city")
              .prefetch_related("photos")
              .order_by("-created_at"))
        return qs


class CarDetailView(DetailView):
    model = Car
    template_name = "cars/car_detail.html"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (Car.objects.filter(is_active=True)
                .select_related("brand", "model_name", "place", "place__city")  # pas place__region !
                .prefetch_related("photos"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        car = self.object

        photos_qs = car.photos.all().order_by("-is_cover", "order", "id")
        photos = [p for p in photos_qs if getattr(p.image, "name", "")]

        cover = next((p for p in photos if p.is_cover), photos[0] if photos else None)

        display_photos = []
        if cover:
            display_photos.append(cover)
        display_photos += [p for p in photos if not cover or p.pk != cover.pk]

        similar = (Car.objects
                   .filter(is_active=True, place__region=car.place.region)
                   .exclude(pk=car.pk)
                   .select_related("place", "place__city")
                   .prefetch_related("photos")
                   .order_by("-created_at")[:8])

        ctx.update({
            "cover": cover,
            "photos": display_photos,
            "similar_cars": similar,
        })
        return ctx


@login_required
@require_POST
def favorite_toggle(request, slug):
    car = get_object_or_404(Car, slug=slug, is_active=True)

    if car.owner_id == request.user.id:
        return HttpResponseBadRequest("Vous ne pouvez pas ajouter votre propre annonce aux favoris.")

    fav, created = Favorite.objects.get_or_create(user=request.user, car=car)
    if not created:
        fav.delete()
        state = "removed"
    else:
        state = "added"

    count = car.favorite_links.count()

    # AJAX ?
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or \
       "application/json" in request.headers.get("Accept", ""):
        return JsonResponse({"status": state, "count": count})

    return redirect(request.META.get("HTTP_REFERER", car.get_absolute_url()))


@login_required
def my_favorites(request):
    cars = (Car.objects
            .filter(favorite_links__user=request.user)
            .select_related("brand", "place__city")
            .prefetch_related(Prefetch("photos",
                queryset=CarPhoto.objects.order_by("order", "id"),
                to_attr="prefetched_photos"))
            .annotate(favorite_count=Count("favorite_links", distinct=True))
            .order_by("-favorite_links__created_at"))
    return render(request, "cars/account_favorites.html", {"cars": cars})