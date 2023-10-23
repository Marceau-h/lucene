import pandas as pd

with open("produits.csv", encoding="utf-8") as f:
    df = pd.read_csv(f, sep=",")

df.to_xml("produits.xml", root_name="produits", row_name="produit")
