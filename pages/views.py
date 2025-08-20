from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Exists, OuterRef, BooleanField, Value, Prefetch
from cars.models import Car, CarPhoto, Favorite

from .models import LandingPage, LandingKind
from .forms import CarSearchForm

# Create your views here.
def home(request):
    form = CarSearchForm(request.GET or None)
    user = request.user if request.user.is_authenticated else None
    fav_exists = Favorite.objects.filter(user=user, car=OuterRef("pk")) if user else Favorite.objects.none()

    base_qs = (
        Car.objects.filter(is_active=True)
        .select_related("brand", "place__city")
        .prefetch_related(
            Prefetch(
                "photos",
                queryset=CarPhoto.objects.order_by("order", "id"),
                to_attr="prefetched_photos",  # si tu utilises cover_photo basé sur photos
            )
        )
        .annotate(
            favorite_count=Count("favorite_links", distinct=True),
            is_favorite=Exists(fav_exists) if user else Value(False, output_field=BooleanField()),
        )
        .order_by("-created_at")
    )

    latest_cars = base_qs[:12]
    top_cars = base_qs.order_by("-is_featured", "-created_at")[:3]  # adapte si tu as un flag is_featured

    return render(request, "pages/index.html", {
        "latest_cars": latest_cars,
        "top_cars": top_cars,
        "search_form": form,
    })


def landing_page(request, slug):
    page = get_object_or_404(LandingPage, slug=slug, is_active=True)

    cars = None
    if page.kind != LandingKind.STATIC:
        cars = (Car.objects.filter(is_active=True)
                .select_related("brand", "place__city")
                .prefetch_related(Prefetch("photos",
                                           queryset=CarPhoto.objects.order_by("order", "id"),
                                           to_attr="prefetched_photos"))
                .order_by("-created_at"))
        if page.kind == LandingKind.DESTINATION and page.city_id:
            cars = cars.filter(place__city_id=page.city_id)
        elif page.kind == LandingKind.REGION and page.region:
            cars = cars.filter(place__region=page.region)
        elif page.kind == LandingKind.CATEGORY and page.body_type:
            cars = cars.filter(body_type=page.body_type)
    context = {"page": page, "cars": cars}
    return render(request, "pages/landing_page.html", context)


def cars_search(request):
    return render(request, "pages/search_car.html")