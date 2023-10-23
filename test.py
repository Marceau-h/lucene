import pandas as pd

df = pd.read_csv("test.csv", sep=";")

df.to_csv("test2.csv", sep=",")
