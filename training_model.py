import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
import joblib

# Load the data
df = pd.read_csv('Medicalpremium.csv')

# Define numeric features for preprocessing
numeric_features = ['Age', 'Diabetes', 'BloodPressureProblems', 'AnyTransplants',
                    'AnyChronicDiseases', 'Height', 'Weight', 'KnownAllergies',
                    'HistoryOfCancerInFamily', 'NumberOfMajorSurgeries']

# Define preprocessor
numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
preprocessor = ColumnTransformer(transformers=[('num', numeric_transformer, numeric_features)])

# Split the data into features (X) and target (y)
X = df.drop(columns='PremiumPrice')
y = df['PremiumPrice']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=10)

# Create a pipeline with the preprocessor and RandomForestRegressor
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=10))
])

# Train the model
model_pipeline.fit(X_train, y_train)

# Save the trained model
joblib.dump(model_pipeline, 'premium_model.pkl')

print("Model training completed and saved as 'premium_model.pkl'.")
