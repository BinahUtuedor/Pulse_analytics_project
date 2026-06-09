import pandas as pd
df=pd.read_csv('data/raw/taxpayer_data.csv')
df=df.drop_duplicates()
df=df[(df.declared_income>0)&(df.business_turnover>0)]
df.to_csv('data/processed/clean_data.csv',index=False)
