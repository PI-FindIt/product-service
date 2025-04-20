import pandas as pd
from collections import defaultdict
from categories_dicts import categories_keywords_kw_only, brands_keywords
import psycopg2
df = pd.read_sql("SELECT * FROM productmodel WHERE brand_name IS NULL", "postgresql://postgres:postgres@product-service_postgres:5432")

category_keywords = brands_keywords


# Função para encontrar a melhor categoria
def find_category(row):
    scores = defaultdict(int)
    text = ' '.join([str(row['name']), str(row['generic_name']), ' '.join(row['keywords'])]).lower()

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1

    if scores:
        return max(scores, key=scores.get)
    return None


df['brand_name'] = df.apply(find_category, axis=1)

print(df)
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="product-service_postgres",
    port="5432"
)

cur = conn.cursor()

for index, row in df.iterrows():
    if row['brand_name'] is not None:
        cur.execute(
            "UPDATE productmodel SET brand_name = %s WHERE ean = %s",
            (row['brand_name'], row['ean'])
        )

# Commit as alterações e fechar conexões
conn.commit()
cur.close()
conn.close()

print("Categories updated successfully")

