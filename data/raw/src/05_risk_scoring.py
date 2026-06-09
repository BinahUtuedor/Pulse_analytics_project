import pandas as pd, joblib
df=pd.read_csv('data/processed/features.csv')
m=joblib.load('reports/risk_model.pkl')
X=df[['income_ratio','late_filings','previous_investigations']]
df['risk_probability']=m.predict_proba(X)[:,1]
df.to_csv('reports/risk_scores.csv',index=False)
