from django.db import models
from django.utils.translation import gettext_lazy as _


# Choices for car body types
class CarSeat(models.TextChoices):
    TWO = "2", _("2 places")
    THREE = "3", _("3 places")
    FOUR = "4", _("4 places")
    FIVE = "5", _("5 places")
    SIX = "6", _("6 places")
    SEVEN = "7", _("7 places")
    EIGHT = "8", _("8 places")
    NINE = "9", _("9 places")


class CarDoor(models.TextChoices):
    TWO = "2", _("2 portes")
    THREE = "3", _("3 portes")
    FOUR = "4", _("4 portes")
    FIVE = "5", _("5 portes")


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

class CarYear(models.IntegerChoices):
    YEAR_2024 = 2024, _("2024")
    YEAR_2023 = 2023, _("2023")
    YEAR_2022 = 2022, _("2022")
    YEAR_2021 = 2021, _("2021")
    YEAR_2020 = 2020, _("2020")
    YEAR_2019 = 2019, _("2019")
    YEAR_2018 = 2018, _("2018")
    YEAR_2017 = 2017, _("2017")
    YEAR_2016 = 2016, _("2016")
    YEAR_2015 = 2015, _("2015")
    YEAR_2014 = 2014, _("2014")
    YEAR_2013 = 2013, _("2013")
    YEAR_2012 = 2012, _("2012")
    YEAR_2011 = 2011, _("2011")
    YEAR_2010 = 2010, _("2010")
    OTHER_YEAR = 9999, _("Autre année")  # For custom years


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