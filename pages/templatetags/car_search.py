# cars/templatetags/car_search.py
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch
from cars.models import Car, CarPhoto, BodyType, SenegalRegion
from pages.forms import CarSearchForm

register = template.Library()

def _default_qs():
    return (
        Car.objects.filter(is_active=True)
        .select_related("brand", "place__city")
        .prefetch_related(
            Prefetch("photos",
                     queryset=CarPhoto.objects.order_by("order", "id"),
                     to_attr="prefetched_photos")
        )
        .order_by("-created_at")
    )

@register.simple_tag(takes_context=True)
def car_search_context(context, base_qs=None, limit=None, paginate=False, per_page=12):
    request = context.get("request")
    form = CarSearchForm(request.GET or None)

    base_qs = base_qs or _default_qs()
    qs = base_qs

    body_type = region = None
    body_type_label = region_label = None

    if form.is_valid():
        body_type = form.cleaned_data.get("body_type")
        region = form.cleaned_data.get("region")

        if body_type:
            qs = qs.filter(body_type=body_type)
            body_type_label = dict(BodyType.choices).get(body_type)

        if region:
            qs = qs.filter(place__region=region)
            region_label = dict(SenegalRegion.choices).get(region)

    if limit and not paginate:
        qs = qs[:limit]

    no_results = not qs.exists()

    suggest_same_region = base_qs.filter(place__region=region)[:8] if no_results and region else []
    suggest_same_body   = base_qs.filter(body_type=body_type)[:8] if no_results and body_type else []

    # Pagination (optionnelle)
    page_obj = None
    cars_items = qs
    is_paginated = False
    if paginate:
        paginator = Paginator(qs, per_page)
        page_number = (request.GET.get("page") if request else None) or 1
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        cars_items = page_obj.object_list
        is_paginated = paginator.num_pages > 1

    return {
        "form": form,
        "qs": qs,
        "cars": cars_items,
        "page_obj": page_obj,
        "is_paginated": is_paginated,
        "no_results": no_results,
        "body_type_label": body_type_label,
        "region_label": region_label,
        "suggest_same_region": suggest_same_region,
        "suggest_same_body": suggest_same_body,
    }

@register.inclusion_tag("cars/_search_box.html", takes_context=True)
def car_search_box(context, action_url=None, submit_label="Rechercher"):
    request = context.get("request")
    form = CarSearchForm(request.GET or None)
    return {
        "form": form,
        "action_url": action_url or (request.path if request else ""),
        "submit_label": submit_label,
    }
