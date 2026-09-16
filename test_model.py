import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings

df = pd.read_csv('training_dataset.csv')
imputer = SimpleImputer(strategy='median')
df['transaction_amount'] = imputer.fit_transform(df[['transaction_amount']])
X = df.drop(columns=['transaction_id', 'is_fraud'])
y = df['is_fraud']

split_index = int(len(df) * 0.7)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    log_reg = LogisticRegression(class_weight='balanced', random_state=42, solver='liblinear')
    log_reg.fit(X_train_scaled, y_train)
    if len(w) == 0:
        print("liblinear finished without warning!")
    else:
        for warning in w:
            print("Warning:", warning.message)
