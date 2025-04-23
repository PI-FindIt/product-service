from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel


class Name(BaseModel):
    en: str
    pt: str


with open("../migrations/inserts.sql", "r") as file:
    lines = file.readlines()

prompt = """
You are a professional translator. Your task is to translate a given input string into **English (US)** and **European Portuguese (Portugal)**. Follow these rules strictly:

1. **Input Language Detection & Translation Logic**
   - **If the input is English (US):**
     - Preserve the original English text.
     - Translate **only** to European Portuguese (Portugal).
   - **If the input is Portuguese (any variant):**
     - Preserve the original Portuguese text but **convert regional terms to European Portuguese** (e.g., "bolacha" instead of "biscoito").
     - Translate **only** to English (US).
   - **If the input is in another language (e.g., Spanish, French):**
     - Translate it to **both** English (US) and European Portuguese (Portugal).

2. **Output Format**
   - Return **only** the two translations, in this order:
     `English (US)`
     `Portuguese (Portugal)`
   - **No explanations, labels, or extra text**.

3. **European Portuguese Enforcement**
   - Use **exclusively** Portugal-specific vocabulary, spelling, and grammar (e.g., "sumo" not "suco," "pequeno-almoço" not "café da manhã").

**Do not deviate from these rules.** Prioritize linguistic accuracy and regional specificity.
"""

new_lines = []

for line in lines:
    line_strip = line.lstrip(
        "INSERT INTO productmodel (ean, name, generic_name, nutri_score, ingredients, quantity, unit, keywords, images, nutrition, category_name, brand_name) VALUES  ("
    ).rstrip(");\n")

    line_content = line_strip.split("', '")

    original_name = line_content[1].replace("'", "")
    original_generic_name = line_content[2].replace("'", "")

    print("\n\nFetching translation for:", original_name)

    line_new = "INSERT INTO productmodel (ean, name, name_en, generic_name, generic_name_en, nutrition, nutri_score, ingredients, quantity, unit, keywords, images, brand_name, category_name) VALUES ("
    line_new += line_content[0] + "', "

    for k, original in [
        ("name", original_name),
        ("generic_name", original_generic_name),
    ]:
        if original == "":
            print(f" - Skipping {k} since it is empty")
            line_new += "'', '', "
            continue

        print(f" - Fetching {k}")

        response: ChatResponse = chat(
            model="gemma3:4b-it-qat",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": original,
                },
            ],
            format=Name.model_json_schema(),
        )
        if response.message.content is None:
            print("No response from the model.")
            continue

        response_model = Name.model_validate_json(response.message.content)
        print("   Response:", response_model)
        line_new += f"'{response_model.pt.replace("'", "''")}', '{response_model.en.replace("'", "''")}', "

    line_new += "'"
    line_new += "', '".join(line_content[3:])
    line_new += ");\n"
    new_lines.append(line_new)

with open("../migrations/translate.sql", "w") as file:
    file.writelines(new_lines)
