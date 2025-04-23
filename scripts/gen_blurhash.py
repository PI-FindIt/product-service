import blurhash
import requests

from io import BytesIO
from PIL import Image

with open("../migrations/inserts.sql", "r") as file:
    lines = file.readlines()

new_lines: list[str] = []


def build_sql(line_strip: str, blurhash: str | None = None) -> str:
    line_new = "INSERT INTO productmodel (blurhash, ean, name, name_en, generic_name, generic_name_en, nutrition, nutri_score, ingredients, quantity, unit, keywords, images, brand_name, category_name) VALUES ("
    line_new += f"'{blurhash.replace(":", "\:")}'" if blurhash else "NULL"
    line_new += ", "
    line_new += line_strip
    line_new += ");\n"
    return line_new


for line in lines:
    line_strip = line.lstrip(
        "INSERT INTO productmodel (ean, name, name_en, generic_name, generic_name_en, nutrition, nutri_score, ingredients, quantity, unit, keywords, images, brand_name, category_name) VALUES ("
    ).rstrip(");\n")

    line_content = line_strip.split("', '")
    images_str = line_content[11].replace("'", "").lstrip("{").rstrip("}")

    if images_str == "":
        print(f"Ignoring {line_content[0]} since images is empty")
        new_lines.append(build_sql(line_strip, None))
        continue

    url_partial = images_str.split(",")[0].lstrip(
        "https://images.openfoodfacts.org/images/products/"
    )
    url = f"http://192.168.1.2:8000/product/{url_partial}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching image {url}: {response.status_code}")
        new_lines.append(build_sql(line_strip, None))
        continue

    print(line_content[0], response.status_code)

    with Image.open(BytesIO(response.content)) as image:
        image.thumbnail((100, 100))
        hash = blurhash.encode(image, x_components=4, y_components=3)

    new_lines.append(build_sql(line_strip, hash))

with open("../migrations/blurhash.sql", "w") as file:
    file.writelines(new_lines)
