from dataclasses import dataclass
from enum import Enum
import json
import re

all_categories: list["Category"] = []


class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


@dataclass
class Nutrition:
    saturatedFat: str
    fat: str
    salt: str
    sugars: str


@dataclass
class Product:
    ean: str
    name: str
    genericName: str
    nutrition: object
    nutriScore: NutriScore
    ingredients: list[str]
    quantity: str
    unit: str
    keywords: list[str]
    brands: list[str]



@dataclass
class Category:
    name: str
    products: list[Product]
    subcategories: list["Category"]


keys = [
    ("code", "code"),
    ("nutrient_levels", "nutrient_levels"),
    ("nutrition_grades", "nutrition_grades"),
    ("categories", "categories"),
    ("compared_to_category", "compared_to_category"),
    ("quantity", "quantity"),
    ("product_quantity_unit", "product_quantity_unit"),
    ("food_groups_tags", "food_groups_tags"),
    ("ingredients_text_pt", "ingredients_text"),
    ("_keywords", "_keywords"),
    ("product_name_pt", "product_name"),
    ("categories_tags", "categories_tags"),
    ("brands", "brands"),
    ("brands_tags", "brands_tags"),
    ("generic_name_pt", "generic_name"),
    # NOVO
    # after that filter inside by front_pt or front_en, and ingredients_en or ingredients_pt
    ("images", "images"),
    ("nutriments", "nutriments"),
    ("stores", "stores"),
]

all_data = json.load(open("export.json"))
d = []

for product in all_data:
    product_data = {}
    for a, b in keys:
        try:
            if a not in product:
                product[a] = product.pop(b)
            if a == "images":
                ## images is a dict of dicts, i just want 2 images and the rev and the full thing
                images = {}
                l = product[a]
                front_img = "front_pt" if "front_pt" in l else "front_en"
                ingredients_img = (
                    "ingredients_pt" if "ingredients_pt" in l else "ingredients_en"
                )
                code = f"{(13-len(product["code"]))*"0"}{product["code"]}"  # ean
                # /^(...)(...)(...)(.*)$/
                regex = re.compile("^(...)(...)(...)(.*)$")
                code = regex.match(code)
                code = code.groups()
                code = f"https://images.openfoodfacts.org/images/products/{code[0]}/{code[1]}/{code[2]}/{code[3]}/"

                # split it in the following way

                images["front_image"] = (
                    f"{code}{front_img}.{l[front_img]['rev']}.full.jpg"
                )
                images["ingredients_image"] = (
                    f"{code}{ingredients_img}.{l[ingredients_img]['rev']}.full.jpg"
                )
                product[a] = images
            if a == "stores":
                product[a] = product[a].split(",")

            product_data[b] = product[a]

        except KeyError:
            continue
    d.append(product_data)

json.dump(d, open("filtered.json", "w"), indent=2, ensure_ascii=False)
print("All data len:", len(d))
