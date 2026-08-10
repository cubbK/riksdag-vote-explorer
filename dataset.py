import json
import polars as pl

with open("datasets/personlista.json", encoding="utf-8") as f:
    data = json.load(f)

records = []
for entry in data["personlista"]:
    person_list = entry.get("person", [])
    # Each person's fields are stored as a list of single-key dicts
    fields = {k: v for d in person_list if isinstance(d, dict) for k, v in d.items()}
    first = fields.get("tilltalsnamn", "")
    last = fields.get("efternamn", "")
    if first or last:
        records.append({
            "first_name": first,
            "last_name": last,
            "party": fields.get("parti", ""),
            "constituency": fields.get("valkrets", ""),
        })

df = pl.DataFrame(records)
print(df)
