from django.db import models
from django.utils.translation import gettext_lazy as _


# Choices for car body types
class BodyType(models.TextChoices):
    CITY_CAR = "city", _("Citadine")
    SEDAN = "sedan", _("Berline")
    SUV = "suv", "SUV"
    FOUR_BY_FOUR = "4x4", _("4x4")
    PICKUP = "pickup", _("Pickup")
    VAN = "van", _("Monospace / Van")
    MINIBUS = "minibus", _("Minibus")
    BUS = "bus", _("Bus")
    CAR = "car", _("Car")
    COUPE = "coupe", _("Coupé")
    CONVERTIBLE = "conv", _("Cabriolet")
    OTHER = "other", _("Autre")


# Choices for car fuel types
class FuelType(models.TextChoices):
    GASOLINE = "gasoline", _("Essence")
    DIESEL = "diesel", _("Diesel")
    HYBRID = "hybrid", _("Hybride")
    ELECTRIC = "electric", _("Électrique")
    LPG = "lpg", "GPL"
    OTHER = "other", _("Autre")


class Transmission(models.TextChoices):
    MANUAL = "manual", _("Manuelle")
    AUTO = "auto", _("Automatique")

# Choices Regions of Senegal
# https://en.wikipedia.org/wiki/Regions_of_Senegal
class SenegalRegion(models.TextChoices):
    DAKAR = "Dakar", _("Dakar")
    THIES = "Thiès", _("Thiès")
    DIOURBEL = "Diourbel", _("Diourbel")
    KAOLACK = "Kaolack", _("Kaolack")
    FATICK = "Fatick", _("Fatick")
    KAFFRINE = "Kaffrine", _("Kaffrine")
    LOUGA = "Louga", _("Louga")
    SAINT_LOUIS = "Saint-Louis", _("Saint-Louis")
    MATAM = "Matam", _("Matam")
    TAMBACOUNDA = "Tambacounda", _("Tambacounda")
    KEDOUGOU = "Kédougou", _("Kédougou")
    KOLDA = "Kolda", _("Kolda")
    SEDHIOU = "Sédhiou", _("Sédhiou")
    ZIGUINCHOR = "Ziguinchor", _("Ziguinchor")


class CarColor(models.TextChoices):
    WHITE = "white", _("Blanc")
    BLACK = "black", _("Noir")
    SILVER = "silver", _("Argent")
    GREY = "grey", _("Gris")
    BLUE = "blue", _("Bleu")
    RED = "red", _("Rouge")
    GREEN = "green", _("Vert")
    YELLOW = "yellow", _("Jaune")
    ORANGE = "orange", _("Orange")
    BROWN = "brown", _("Marron")
    BEIGE = "beige", _("Beige")
    GOLD = "gold", _("Doré")
    PURPLE = "purple", _("Violet")
    OTHER = "other", _("Autre")


COLOR_HEX = {
    CarColor.WHITE:  "#ffffff",
    CarColor.BLACK:  "#000000",
    CarColor.SILVER: "#c0c0c0",
    CarColor.GREY:   "#808080",
    CarColor.BLUE:   "#1e73be",
    CarColor.RED:    "#d32f2f",
    CarColor.GREEN:  "#2e7d32",
    CarColor.YELLOW: "#fbc02d",
    CarColor.ORANGE: "#fb8c00",
    CarColor.BROWN:  "#795548",
    CarColor.BEIGE:  "#f5f5dc",
    CarColor.GOLD:   "#d4af37",
    CarColor.PURPLE: "#7b1fa2",
    CarColor.OTHER:  "#9e9e9e",
}


COLOR_HEX_BY_VALUE = {k.value: v for k, v in COLOR_HEX.items()}