# pages/context_processors.py
from .models import LandingPage, LandingKind

def landing(request):
    pages = list(
        LandingPage.objects
        .filter(is_active=True)
        .only("id", "title", "slug", "kind", "position")
        .order_by("position", "title")
    )
    return {
        "lp_destinations": [p for p in pages if p.kind == LandingKind.DESTINATION],
        "lp_regions":      [p for p in pages if p.kind == LandingKind.REGION],
        "lp_categories":   [p for p in pages if p.kind == LandingKind.CATEGORY],
        "lp_static":       [p for p in pages if p.kind == LandingKind.STATIC],
    }
