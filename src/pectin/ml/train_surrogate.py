import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import json
import os

def train():
    dataset_path = 'artifacts/synthetic/synthetic_dataset.csv'
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Run generate_dataset.py first.")
    
    print("Loading synthetic dataset...")
    df = pd.read_csv(dataset_path)
    
    # Define features and targets for V1
    features = ['temperature', 'pH', 'time_min']
    targets = ['Y_GalA_product', 'final_DE_product', 'final_Mw_product']
    
    X = df[features]
    Y = df[targets]
    
    print("Splitting data (80/20)...")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
    print("Training Multi-Output Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, Y_train)
    
    print("Evaluating...")
    Y_pred = model.predict(X_test)
    
    metrics = {}
    for i, target_name in enumerate(targets):
        r2 = float(r2_score(Y_test.iloc[:, i], Y_pred[:, i]))
        mse = float(mean_squared_error(Y_test.iloc[:, i], Y_pred[:, i]))
        metrics[target_name] = {'R2': r2, 'MSE': mse}
        print(f"[{target_name}] R^2: {r2:.4f}, MSE: {mse:.4f}")
    
    # Feature importance
    print("\nFeature Importances (Combined for all targets):")
    importances = {}
    for feat, imp in zip(features, model.feature_importances_):
        importances[feat] = float(imp)
        print(f"  {feat}: {imp:.4f}")
    
    model_path = 'artifacts/models/rf_v1.joblib'
    joblib.dump(model, model_path)
    print(f"\nSaved trained surrogate model to {model_path}")
    
    metadata = {
        'simulator_version': 'V1.3',
        'features': features,
        'targets': targets,
        'metrics': metrics,
        'feature_importances': importances
    }
    
    metadata_path = 'artifacts/models/rf_v1_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Saved metadata to {metadata_path}")

if __name__ == '__main__':
    train()
