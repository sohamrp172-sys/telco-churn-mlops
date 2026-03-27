import pandas as pd

INPUT = "WA_Fn-UseC_-Telco-Customer-Churn.csv"

splits = [
    ("data/raw/telco_v1.csv", slice(0, 2333)),
    ("data/raw/telco_v2.csv", slice(0, 4666)),
    ("data/raw/telco_v3.csv", slice(None)),
]

df = pd.read_csv(INPUT)

for path, s in splits:
    subset = df.iloc[s]
    subset.to_csv(path, index=False)
    print(f"{path}: {len(subset)} rows")
