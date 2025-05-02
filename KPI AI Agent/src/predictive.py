import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

def train_predictive_model(df, features, target):
    """
    Train a RandomForestRegressor on the specified features and target.
    Returns the trained model and the mean squared error on the test set.
    """
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    return model, mse

if __name__ == '__main__':
    # Test predictive modeling
    df = pd.read_csv('../data/cases_Q1_current_year.csv')
    features = ['case_complexity', 'staff_experience', 'process_efficiency']  # ensure these columns exist
    target = 'resolution_time'
    
    model, mse = train_predictive_model(df, features, target)
    print("Mean Squared Error:", mse)
