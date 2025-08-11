from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from getpass import getpass

from cars.models import City, Place, Brand, CarModel, CarFeature, Car
from cars.choices_types import CarColor, BodyType, Transmission, FuelType, SenegalRegion

User = get_user_model()

class Command(BaseCommand):
    help = "Charge 3 voitures d'exemple + données de base (marques, modèles, lieux)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email du propriétaire des annonces (CustomUser).")
        parser.add_argument("--create-if-missing", action="store_true",
                            help="Crée le compte s'il n'existe pas encore (champs requis nécessaires).")
        # Champs requis si on crée le compte
        parser.add_argument("--first-name", help="Prénom (requis si --create-if-missing).")
        parser.add_argument("--last-name", help="Nom (requis si --create-if-missing).")
        parser.add_argument("--user-type", choices=["HOMME", "FEMME"], help="Type utilisateur.")
        parser.add_argument("--phone", help="Téléphone au format international, ex: +221771234567")
        # Mot de passe (facultatif) : prompt si création et non fourni
        parser.add_argument("--password", help="Mot de passe pour création ou reset (optionnel).")
        parser.add_argument("--reset-password", action="store_true",
                            help="Ré-initialise le mot de passe si l'utilisateur existe déjà.")

    def handle(self, *args, **o):
        email = o["email"].strip().lower()

        # 1) Récupérer / créer l'utilisateur
        try:
            owner = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f"Utilisateur existant trouvé: {owner} ({owner.email})"))
            if o["reset_password"]:
                pwd = o.get("password") or getpass("Nouveau mot de passe (saisie masquée) : ")
                owner.set_password(pwd)
                owner.save()
                self.stdout.write(self.style.WARNING("Mot de passe ré-initialisé."))
        except User.DoesNotExist:
            if not o["create_if_missing"]:
                raise CommandError(
                    f"L'utilisateur avec l'email {email} n'existe pas. "
                    f"Ajoute --create-if-missing et fournis les champs requis."
                )
            # Vérifs champs requis
            missing = [k for k in ("first_name", "last_name", "user_type", "phone") if not o.get(k.replace("-", "_"))]
            if missing:
                raise CommandError(f"Champs requis manquants pour créer le compte : {', '.join(missing)}.")
            pwd = o.get("password") or getpass("Mot de passe (saisie masquée) : ")
            owner = User.objects.create_user(
                email=email,
                first_name=o["first_name"],
                last_name=o["last_name"],
                user_type=o["user_type"],
                phone_number=o["phone"],
                password=pwd,
            )
            self.stdout.write(self.style.SUCCESS(f"Utilisateur créé: {owner} ({owner.email})"))

        # 2) Villes + Places
        cities_data = [
            ("Dakar", SenegalRegion.DAKAR),
            ("Thiès", SenegalRegion.THIES),
            ("Saint-Louis", SenegalRegion.SAINT_LOUIS),
        ]
        city_objs = {}
        for name, region in cities_data:
            city, _ = City.objects.get_or_create(name=name)
            city_objs[name] = city
            Place.objects.get_or_create(city=city, region=region)

        # 3) Marques + Modèles
        brands_models = {
            "Toyota": ["Corolla", "Hilux"],
            "Hyundai": ["Tucson"],
            "Peugeot": ["301"],
        }
        brand_objs = {}
        for brand, models in brands_models.items():
            b, _ = Brand.objects.get_or_create(name=brand)
            brand_objs[brand] = b
            for m in models:
                CarModel.objects.get_or_create(brand=b, name=m)

        # 4) Caractéristiques
        features_list = ["Climatisation", "GPS intégré", "Caméra de recul", "Bluetooth"]
        feature_objs = {name: CarFeature.objects.get_or_create(name=name)[0] for name in features_list}

        # 5) 3 voitures d'exemple (sans photos)
        examples = [
            {
                "title": "Toyota Corolla 2020 - Propre et Climatisée",
                "brand": "Toyota", "model": "Corolla", "year": 2020,
                "body_type": BodyType.SEDAN, "transmission": Transmission.MANUAL,
                "fuel_type": FuelType.GASOLINE, "seats": 5, "doors": 4,
                "mileage_km": 25000, "color": CarColor.WHITE,
                "features": ["Climatisation", "Bluetooth"],
                "place": ("Dakar", SenegalRegion.DAKAR), "daily_price": 25000,
            },
            {
                "title": "Hyundai Tucson 2022 - SUV de Luxe",
                "brand": "Hyundai", "model": "Tucson", "year": 2022,
                "body_type": BodyType.SUV, "transmission": Transmission.AUTO,
                "fuel_type": FuelType.DIESEL, "seats": 5, "doors": 4,
                "mileage_km": 15000, "color": CarColor.BLACK,
                "features": ["Climatisation", "GPS intégré", "Caméra de recul"],
                "place": ("Thiès", SenegalRegion.THIES), "daily_price": 40000,
            },
            {
                "title": "Peugeot 301 2019 - Économique et Confortable",
                "brand": "Peugeot", "model": "301", "year": 2019,
                "body_type": BodyType.SEDAN, "transmission": Transmission.MANUAL,
                "fuel_type": FuelType.DIESEL, "seats": 5, "doors": 4,
                "mileage_km": 30000, "color": CarColor.SILVER,
                "features": ["Climatisation", "Bluetooth"],
                "place": ("Saint-Louis", SenegalRegion.SAINT_LOUIS), "daily_price": 20000,
            },
        ]

        created_count = 0
        for c in examples:
            place = Place.objects.get(city__name=c["place"][0], region=c["place"][1])
            brand = brand_objs[c["brand"]]
            model = CarModel.objects.get(brand=brand, name=c["model"])

            car, created = Car.objects.get_or_create(
                owner=owner,
                title=c["title"],
                brand=brand,
                model_name=model,
                year=c["year"],
                body_type=c["body_type"],
                transmission=c["transmission"],
                fuel_type=c["fuel_type"],
                seats=c["seats"],
                doors=c["doors"],
                mileage_km=c["mileage_km"],
                color=c["color"],
                place=place,
                daily_price=c["daily_price"],
                defaults={"description": "Voiture bien entretenue et prête à l'emploi."}
            )
            if created:
                car.features.set([feature_objs[f] for f in c["features"]])
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Ajouté: {car.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Déjà présent: {car.title}"))

        self.stdout.write(self.style.SUCCESS(f"=== Terminé. Nouveaux véhicules: {created_count} ==="))
