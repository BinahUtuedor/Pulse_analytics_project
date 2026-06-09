import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
df=pd.read_csv('data/processed/features.csv')
X=df[['income_ratio','late_filings','previous_investigations']]
y=df['high_risk']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42)
m=LogisticRegression()
m.fit(Xtr,ytr)
joblib.dump(m,'reports/risk_model.pkl')
print('Model trained')
