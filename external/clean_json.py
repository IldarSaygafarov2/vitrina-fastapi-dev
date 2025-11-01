import json
import re

# Чтение "испорченного" JSON-файла как обычного текста
with open('buy_6_output_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data)



