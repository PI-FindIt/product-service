import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

all_categories: list["Category"] = []
all_brands: list["Brand"] = []


class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT-APPLICABLE"


@dataclass
class Nutrition:
    saturated_fat: str
    fat: str
    salt: str
    sugars: str


@dataclass
class Product:
    ean: str
    name: str
    generic_name: str
    nutrition: Nutrition
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str]
    stores: list[str]
    images: dict[str, str]
    nutriments: dict[str, str]

    def __str__(self):
        # make it json
        return json.dumps(self.__dict__.__str__(), indent=4)

    def __hash__(self):
        return hash(self.name + self.ean)


@dataclass
class Category:
    name: str
    products: list[Product]
    subcategories: list["Category"]
    parent: Optional["Category"] = None

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def __hash__(self):
        return hash(self.name)


@dataclass
class Brand:
    name: str
    products: list[Product]
    subbrands: list["Brand"]
    parent: Optional["Brand"] = None

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def __hash__(self):
        return hash(self.name)


def find_or_create_category(
    category_name: str, parent: Optional[Category] = None
) -> Category:
    # Check if category exists under parent
    if parent:
        for subcat in parent.subcategories:
            if subcat.name == category_name:
                return subcat
    else:
        # Check root categories
        for cat in all_categories:
            if cat.parent is None and cat.name == category_name:
                return cat

    # Create new category
    new_cat = Category(name=category_name, products=[], subcategories=[], parent=parent)
    all_categories.append(new_cat)
    if parent:
        parent.subcategories.append(new_cat)
    return new_cat


def find_or_create_brand(brand_name: str, parent: Optional[Brand] = None) -> Brand:
    # Check if brand exists under parent
    if parent:
        for subbrand in parent.subbrands:
            if subbrand.name == brand_name:
                return subbrand
    else:
        # Check root brands
        for br in all_brands:
            if br.parent is None and br.name == brand_name:
                return br

    # Create new brand
    new_br = Brand(name=brand_name, products=[], subbrands=[], parent=parent)
    all_brands.append(new_br)
    if parent:
        parent.subbrands.append(new_br)
    return new_br


def process_categories_hierarchy(category_names: list[str], product: Product) -> None:
    current_parent = None
    terminal_category = None

    for name in category_names:
        current_parent = find_or_create_category(name, current_parent)
        terminal_category = current_parent

    if terminal_category:
        terminal_category.add_product(product)


def process_brands_hierarchy(brand_names: list[str], product: Product) -> None:
    current_parent = None
    terminal_brand = None

    for name in brand_names:
        current_parent = find_or_create_brand(name, current_parent)
        terminal_brand = current_parent

    if terminal_brand:
        terminal_brand.add_product(product)


def load_products_from_json(json_path: str) -> list[Product]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = []
    for item in data:
        # Extract nutrient levels
        nutrient_levels = item.get("nutrient_levels", {})
        nutrition = Nutrition(
            saturated_fat=nutrient_levels.get("saturated-fat", None),
            fat=nutrient_levels.get("fat", None),
            salt=nutrient_levels.get("salt", None),
            sugars=nutrient_levels.get("sugars", None),
        )

        # Create product
        product = Product(
            ean=item["code"],
            name=item.get("product_name", ""),
            generic_name=item.get("generic_name", ""),
            nutrition=nutrition,
            nutri_score=NutriScore(item.get("nutrition_grades", "unknown").upper()),
            ingredients=item.get("ingredients_text", ""),
            quantity=item.get("quantity", ""),
            unit=item.get("product_quantity_unit", ""),
            keywords=item.get("_keywords", []),
            images=item.get("images", {}),
            nutriments=item.get("nutriments", {}),
            stores=item.get("stores", []),
        )

        # Process categories
        raw_categories = item.get("category_tags", [])
        category_names = [
            c.replace("en:", "").strip() for c in raw_categories if c.strip()
        ]
        if category_names:
            process_categories_hierarchy(category_names, product)

        # Process brands
        raw_brands = item.get("brands_tags", [])
        brand_names = [c.replace("en:", "").strip() for c in raw_brands if c.strip()]
        if brand_names:
            process_brands_hierarchy(brand_names[::-1], product)

        products.append(product)

    return products


# ... [Keep all previous code unchanged until main block] ...


def generate_sql_general(products: list[Product]) -> str:
    # Table configuration schema
    table_config = {
        "category": {
            "class": Category,
            "columns": [
                ("id", lambda cat, ctx: ctx["category_ids"][cat]),
                ("name", lambda cat, _: cat.name),
                (
                    "parent_id",
                    lambda cat, ctx: ctx["category_ids"].get(cat.parent, None),
                ),
                (
                    "parent_name",
                    lambda cat, _: cat.parent.name if cat.parent else None,
                ),
            ],
            "sequence": "category_id_seq",
        },
        "brand": {
            "class": Brand,
            "columns": [
                ("id", lambda br, ctx: ctx["brand_ids"][br]),
                ("name", lambda br, _: br.name),
                (
                    "parent_id",
                    lambda br, ctx: ctx["brand_ids"].get(br.parent, None),
                ),
                (
                    "parent_name",
                    lambda br, _: br.parent.name if br.parent else None,
                ),
            ],
            "sequence": "brand_id_seq",
        },
        "productmodel": {
            "class": Product,
            "columns": [
                ("ean", lambda p, _: p.ean),
                ("name", lambda p, _: p.name.replace("\n", " ").replace("\r", "").replace(":", "")),
                (
                    "generic_name",
                    lambda p, _: p.generic_name.replace("\n", " ").replace("\r", "").replace(":", ""),
                ),
                (
                    "nutri_score",
                    lambda p, _: p.nutri_score.value.replace("-", "_") if p.nutri_score else None,
                ),
                (
                    "ingredients",
                    lambda p, _: p.ingredients.replace("\n", " ").replace("\r", "").replace(":", ""),
                ),
                ("quantity", lambda p, _: p.quantity),
                ("unit", lambda p, _: p.unit),
                ("keywords", lambda p, _: p.keywords),
                ("images", lambda p, _: list(p.images.values())),
                ("nutrition", lambda p, _: json.dumps(p.nutriments)),
                (
                    "category_name",
                    lambda p, ctx: ctx["product_category_map"].get(p.name),
                ),
                ("brand_name", lambda p, ctx: ctx["product_brand_map"].get(p.name)),
            ],
            "sequence": "product_ean_seq",
        },
    }

    # Create category mapping and context
    category_ids = {cat: idx + 1 for idx, cat in enumerate(all_categories)}
    category_names = {idx + 1: cat.name for idx, cat in enumerate(all_categories)}
    product_category_map: dict[str, int | str] = {}
    for cat in all_categories:
        for product in cat.products:
            product_category_map[product.ean] = category_ids[cat]
            product_category_map[product.name] = category_names[category_ids[cat]]

    # Create brand mapping and context
    brand_ids = {br: idx + 1 for idx, br in enumerate(all_brands)}
    brand_names = {idx + 1: br.name for idx, br in enumerate(all_brands)}
    product_brand_map: dict[str, int | str] = {}
    for br in all_brands:
        for product in br.products:
            product_brand_map[product.ean] = brand_ids[br]
            product_brand_map[product.name] = brand_names[brand_ids[br]]

    context = {
        "category_ids": category_ids,
        "category_names": category_names,
        "product_category_map": product_category_map,
        "brand_ids": brand_ids,
        "brand_names": brand_names,
        "product_brand_map": product_brand_map,
    }

    # Generate SQL
    sql = []
    csv_categories: list[str] = ["id,name,parent_id,parent_name"]
    csv_brands: list[str] = ["id,name,parent_id,parent_name"]
    #
    # # Create sequences
    # sql.append("-- SEQUENCES")
    # for table, config in table_config.items():
    #     sql.append(f"CREATE SEQUENCE IF NOT EXISTS {config['sequence']};")
    # sql.append("-- TYPE")
    # sql.append(
    #     "CREATE TYPE nutri_score AS ENUM ('A', 'B', 'C', 'D', 'E', 'UNKNOWN', 'NOT-APPLICABLE');",
    # )
    # # Create tables
    # sql.append("\n-- TABLES")
    # sql.append(
    #     """
    # CREATE TABLE category (
    #     id INTEGER PRIMARY KEY DEFAULT nextval('category_id_seq'),
    #     name TEXT NOT NULL,
    #     parent_id INTEGER REFERENCES category(id)
    #     parent_name TEXT references category(name)
    # );
    # CREATE TABLE brand (
    #     id INTEGER PRIMARY KEY DEFAULT nextval('brand_id_seq'),
    #     name TEXT NOT NULL,
    #     parent_id INTEGER REFERENCES brand(id)
    #     parent_name TEXT references brand(name)
    # );
    # CREATE TABLE product (
    #     ean TEXT PRIMARY KEY,
    #     name TEXT NOT NULL,
    #     generic_name TEXT,
    #     nutri_score nutri_score,
    #     ingredients TEXT,
    #     quantity TEXT,
    #     unit TEXT,
    #     keywords TEXT[],
    #     brands TEXT[],
    #     stores TEXT[],
    #     images JSONB,
    #     nutriments JSONB,
    #     terminal_category INTEGER REFERENCES category(name)
    # );
    # """
    # )

    # Generate inserts
    for table, config in table_config.items():
        if table == "category":
            # objects = all_categories
            continue
        elif table == "brand":
            objects = all_brands
            continue
        else:
            objects = products

        # sql.append(f"\n-- {table.upper()} INSERTS")
        for obj in objects:
            if not isinstance(obj, config["class"]):
                continue

            columns = []
            values = []
            for col_name, value_fn in config["columns"]:
                raw_value = value_fn(obj, context)
                if raw_value is None:
                    values.append("NULL")
                elif isinstance(raw_value, list):
                    escaped = [f"'{v.replace("'", "''")}'" for v in raw_value]
                    values.append(
                        f"ARRAY[{', '.join(escaped)}]{"::text[]" if not escaped else ""}"
                    )
                elif isinstance(raw_value, dict):
                    values.append(f"'{json.dumps(raw_value)}'::jsonb")
                else:
                    safe_value = str(raw_value).replace("'", "''")
                    values.append(f"'{safe_value}'")

                columns.append(col_name)

            sql.append(
                f"INSERT INTO {table} ({', '.join(columns)}) "
                f"VALUES ({', '.join(values)});"
            )
            csv_categories.append(f"{','.join(values)}")
            csv_brands.append(f"{','.join(values)}")

    # remove ' from the csv.
    csv_categories = [x.replace("'", "").replace("NULL", "") for x in csv_categories]
    csv_brands = [x.replace("'", "").replace("NULL", "") for x in csv_brands]
    return "\n".join(sql), "\n".join(csv_categories), "\n".join(csv_brands)


# Example usage
if __name__ == "__main__":
    products = load_products_from_json("filtered.json")

    # Print products count
    print(f"Loaded {len(products)} products")

    # Print categories count
    print(f"Loaded {len(all_categories)} categories")

    print(f"Loaded {len(all_brands)} brands")

    # Print categories hierarchy
    def print_category(cat: Category, level: int = 0):
        indent = "  " * level
        print(f"{indent}- {cat.name} ({len(cat.products)} products)")

        for product in cat.products:
            print(f"{indent+indent}  - {product.name}")

        for subcat in cat.subcategories:
            print_category(subcat, level + 1)

    # Print root categories
    for cat in all_categories:
        if cat.parent is None:
            print_category(cat)

    # Print brands hierarchy
    def print_brand(br: Brand, level: int = 0):
        indent = "  " * level
        print(f"{indent}- {br.name} ({len(br.products)} products)")

        for product in br.products:
            print(f"{indent+indent}  - {product.name}")

        for subbr in br.subbrands:
            print_brand(subbr, level + 1)

    # Print root categories
    for br in all_brands:
        if br.parent is None:
            print_brand(br)

    sql_script, csv_cat, csv_brands = generate_sql_general(products)

    # Save to file
    with open("../migrations/inserts.sql", "w", encoding="utf-8") as f:
        f.write(sql_script)

    with open("categories.csv", "w", encoding="utf-8") as f:
        f.write(csv_cat)

    with open("brands.csv", "w", encoding="utf-8") as f:
        f.write(csv_brands)

    print("SQL script generated successfully!")
