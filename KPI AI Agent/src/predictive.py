import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib

def train_predictive_model(
    df: pd.DataFrame,
    features: list,
    target: str,
    categorical_features: list = [],
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple:
    """
    Train a RandomForestRegressor with optional hyperparameter tuning and preprocessing.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        features (list): List of feature column names.
        target (str): Target column name.
        categorical_features (list): List of categorical feature column names.
        test_size (float): Test set proportion.
        random_state (int): Seed for reproducibility.
        
    Returns:
        tuple: (best_model, metrics, feature_importance)
    """
    # Validate input data
    if df.empty:
        raise ValueError("DataFrame is empty")
    if not set(features).issubset(df.columns):
        missing_cols = set(features) - set(df.columns)
        raise ValueError(f"Missing columns: {missing_cols}")
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found")

    # Handle missing values
    df.dropna(subset=features + [target], inplace=True)
    if df.empty:
        raise ValueError("No valid data after dropping missing values")

    X = df[features]
    y = df[target]

    # Preprocess categorical features
    if categorical_features:
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(), categorical_features)
            ],
            remainder='passthrough'
        )
        X = preprocessor.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Hyperparameter tuning
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }
    model = RandomForestRegressor(random_state=random_state)
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    # Evaluate
    predictions = best_model.predict(X_test)
    metrics = {
        "mse": mean_squared_error(y_test, predictions),
        "rmse": mean_squared_error(y_test, predictions, squared=False),
        "mae": mean_absolute_error(y_test, predictions),
        "r2": r2_score(y_test, predictions),
    }

    # Feature importance
    if hasattr(best_model, "feature_importances_"):
        feature_names = (
            preprocessor.get_feature_names_out() 
            if categorical_features else features
        )
        feature_importance = pd.Series(
            best_model.feature_importances_,
            index=feature_names
        ).sort_values(ascending=False)
    else:
        feature_importance = None

    return best_model, metrics, feature_importance

if __name__ == "__main__":
    try:
        # Load data
        df = pd.read_csv('../data/cases_Q1_current_year.csv')
        
        # Define parameters
        features = ['case_complexity', 'staff_experience', 'process_efficiency']
        target = 'resolution_time'
        categorical_features = []  # Add categorical columns here
        
        # Train model
        model, metrics, feature_imp = train_predictive_model(
            df,
            features,
            target,
            categorical_features=categorical_features
        )
        
        # Save model
        joblib.dump(model, 'trained_model.pkl')
        
        # Output results
        print("Evaluation Metrics:")
        for metric, value in metrics.items():
            print(f"{metric.upper()}: {value:.4f}")
        if feature_imp is not None:
            print("\nTop Features by Importance:")
            print(feature_imp.head(5))
            
    except FileNotFoundError:
        print("Error: CSV file not found. Check the path.")
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
