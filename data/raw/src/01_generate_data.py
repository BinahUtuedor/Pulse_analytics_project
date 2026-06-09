import pandas as pd, numpy as np
np.random.seed(42)
n=10000
df=pd.DataFrame({
'taxpayer_id':range(1,n+1),
'declared_income':np.random.normal(45000,15000,n),
'business_turnover':np.random.normal(120000,50000,n),
'late_filings':np.random.poisson(1.5,n),
'previous_investigations':np.random.poisson(0.5,n)
})
df.to_csv('data/raw/taxpayer_data.csv',index=False)
print('Generated')
