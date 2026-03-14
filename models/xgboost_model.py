from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

def train_model(df):
    X = df.drop('target', axis=1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, shuffle=False, test_size=0.2
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,         # Ensure consistent results every time
        eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    return model, X_test, y_test
