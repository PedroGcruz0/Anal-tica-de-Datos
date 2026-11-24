import pandas as pd

tensao = pd.Series([12.6, 12.1, 12.8, 11.9], index=["B1", "B2", "B3", "B4"])
tensao[tensao < 12.4]