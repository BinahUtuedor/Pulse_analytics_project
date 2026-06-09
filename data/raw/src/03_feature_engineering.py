import pandas as pd, numpy as np
df=pd.read_csv('data/processed/clean_data.csv')
df['income_ratio']=df['declared_income']/df['business_turnover']
df['compliance_score']=df['late_filings']*2+df['previous_investigations']*3
df['high_risk']=np.where((df['income_ratio']<0.15)&(df['compliance_score']>4),1,0)
df.to_csv('data/processed/features.csv',index=False)
