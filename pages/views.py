from django.shortcuts import render
from django.db.models import Count, Exists, OuterRef, BooleanField, Value, Prefetch
from cars.models import Car, CarPhoto, Favorite


# Create your views here.
def home(request):
    user = request.user if request.user.is_authenticated else None
    fav_exists = Favorite.objects.filter(user=user, car=OuterRef("pk")) if user else Favorite.objects.none()

    base_qs = (
        Car.objects.filter(is_active=True)
        .select_related("brand", "model_name", "place__city")
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
    })