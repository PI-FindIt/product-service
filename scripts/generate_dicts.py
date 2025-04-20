import psycopg2
from collections import Counter
import re

# Baixar stopwords em português (se necessário)

conn = psycopg2.connect("postgresql://postgres:postgres@product-service_postgres:5432")
cursor = conn.cursor()

#CHANGE BRAND_NAME BY CATEGORY NAME if needed

cursor.execute("SELECT DISTINCT brand_name FROM productmodel WHERE brand_name IS NOT NULL")
categories = [row[0] for row in cursor.fetchall()]

brand_keywords = {}

for brand in categories:
    cursor.execute(f"""
        SELECT 
          name, generic_name, keywords 
        FROM productmodel 
        WHERE brand_name = %s
    """, (brand,))

    all_text = []
    for row in cursor.fetchall():
        name, generic_name, keywords = row
        text = f"{name} {generic_name} {' '.join(keywords)}".lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = re.findall(r'\b\w+\b', text)
        filtered_words = [word for word in words if len(word) > 2]
        all_text.extend(filtered_words)

    word_counts = Counter(all_text)
    top_words = [word for word, count in word_counts.most_common(50)]  # Top 50 palavras

    brand_keywords[brand] = top_words

conn.close()

print(brand_keywords)
