import nbformat as nbf

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Stage 5: Basic Fraud Modelling\nThis notebook fulfills the final practical deliverable for our study path. We will handle missing values, combat class imbalance, perform a time-based train/test split, and evaluate our models using a confusion matrix."),
    
    nbf.v4.new_markdown_cell("## 1. Load Data and Impute Missing Values"),
    nbf.v4.new_code_cell("""import pandas as pd\nfrom sklearn.impute import SimpleImputer\n\n# Load the dataset\ndf = pd.read_csv('training_dataset.csv')\nprint("Original Dataset Shape:", df.shape)\ndisplay(df.head())\n\n# Impute missing values in 'transaction_amount' using the median\nimputer = SimpleImputer(strategy='median')\ndf['transaction_amount'] = imputer.fit_transform(df[['transaction_amount']])\nprint("\\nMissing values after imputation:\\n", df.isnull().sum())\n"""),
    
    nbf.v4.new_markdown_cell("## 2. Feature Selection & Time-Based Split\nTo prevent data leakage, we cannot shuffle the data before splitting. We must simulate the real world where we train on the past and predict on the future."),
    nbf.v4.new_code_cell("""# Drop transaction_id as it has no predictive power\nX = df.drop(columns=['transaction_id', 'is_fraud'])\ny = df['is_fraud']\n\n# Perform a strictly sequential split (no shuffling)\n# First 70% as training, last 30% as test\nsplit_index = int(len(df) * 0.7)\n\nX_train, X_test = X.iloc[:split_index], X.iloc[split_index:]\ny_train, y_test = y.iloc[:split_index], y.iloc[split_index:]\n\nprint("Training set size:", X_train.shape[0])\nprint("Testing set size:", X_test.shape[0])\n"""),
    
    nbf.v4.new_markdown_cell("## 3. Train Baseline Logistic Regression Model\nWe use `class_weight='balanced'` because fraud is rare, so the model needs to penalize missing a fraudster much more heavily than a normal prediction."),
    nbf.v4.new_code_cell("""from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay\nimport matplotlib.pyplot as plt\n\n# Initialize and train the Logistic Regression model\nlog_reg = LogisticRegression(class_weight='balanced', random_state=42)\nlog_reg.fit(X_train, y_train)\n\n# Predict on the test set\ny_pred_log = log_reg.predict(X_test)\n\n# Output evaluation metrics\nprint("--- Logistic Regression Evaluation ---")\nprint(classification_report(y_test, y_pred_log, zero_division=0))\n\n# Plot Confusion Matrix\ncm_log = confusion_matrix(y_test, y_pred_log)\ndisp_log = ConfusionMatrixDisplay(confusion_matrix=cm_log, display_labels=['Legit (0)', 'Fraud (1)'])\ndisp_log.plot(cmap='Blues')\nplt.title("Logistic Regression Confusion Matrix")\nplt.show()\n"""),
    
    nbf.v4.new_markdown_cell("## 4. Train Tree Model (Random Forest)\nTree models often capture non-linear relationships better than linear models."),
    nbf.v4.new_code_cell("""from sklearn.ensemble import RandomForestClassifier\n\n# Initialize and train the Random Forest model\nrf_model = RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42)\nrf_model.fit(X_train, y_train)\n\n# Predict on the test set\ny_pred_rf = rf_model.predict(X_test)\n\n# Output evaluation metrics\nprint("--- Random Forest Evaluation ---")\nprint(classification_report(y_test, y_pred_rf, zero_division=0))\n\n# Plot Confusion Matrix\ncm_rf = confusion_matrix(y_test, y_pred_rf)\ndisp_rf = ConfusionMatrixDisplay(confusion_matrix=cm_rf, display_labels=['Legit (0)', 'Fraud (1)'])\ndisp_rf.plot(cmap='Greens')\nplt.title("Random Forest Confusion Matrix")\nplt.show()\n""")
]

with open('stage5_modelling.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Stage 5 Notebook created successfully.")
