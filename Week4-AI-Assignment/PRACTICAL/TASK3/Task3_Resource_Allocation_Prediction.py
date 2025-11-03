# ==============================================================================
# TASK 3: PREDICTIVE ANALYTICS FOR RESOURCE ALLOCATION
# Dataset: Wisconsin Diagnostic Breast Cancer (WDBC)
# Model: Random Forest Classifier
# Deliverable Components: Preprocessing, Training, Evaluation (Accuracy/F1), Feature Importance
# ==============================================================================

# --- 1. Import Libraries ---
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import matplotlib.pyplot as plt # Added for optional visualization

print("Libraries imported successfully.")

# --- 2. Data Loading and Cleaning ---
try:
    # NOTE: Ensure your dataset file is named 'wdbc_data.csv' and is in the same directory.
    df = pd.read_csv('wdbc_data.csv') 
    print(f"Dataset loaded. Initial shape: {df.shape}")
except FileNotFoundError:
    print("FATAL ERROR: 'wdbc_data.csv' not found. Please check the file path and name.")
    exit() 

# Standard cleaning for WDBC: Drop ID and the redundant last column ('Unnamed: 32')
df = df.drop(['id', 'Unnamed: 32'], axis=1, errors='ignore')


# --- 3. Goal 1: Data Preprocessing (Label Engineering & Splitting) ---

### 3a. Feature Engineering: Creating Multi-Class Target ('priority')
# Convert binary diagnosis (M/B) into three resource allocation levels (High/Medium/Low).
# Logic: Malignant ('M') is always 'High'. Benign ('B') is split based on 'radius_mean' size.
benign_data = df[df['diagnosis'] == 'B']

if not benign_data.empty:
    # Determine the split point for Benign cases using the median radius
    benign_median_radius = benign_data['radius_mean'].median()
    print(f"Calculated Benign Split Threshold (radius_mean): {benign_median_radius:.4f}")

    def assign_priority(row):
        if row['diagnosis'] == 'M':
            return 'High'  # Highest resource need
        elif row['radius_mean'] >= benign_median_radius:
            return 'Medium' # Moderate resource need
        else:
            return 'Low'     # Lowest resource need
    
    df['priority'] = df.apply(assign_priority, axis=1)
    print("\nNew Priority Distribution:")
    print(df['priority'].value_counts())
else:
    print("FATAL ERROR: Could not calculate median radius, as no Benign samples were found.")
    exit()

### 3b. Final Target Encoding and Data Split
le = LabelEncoder()
df['priority_encoded'] = le.fit_transform(df['priority'])
target_names = le.classes_ # Store class names for final reporting (e.g., ['High', 'Low', 'Medium'])
print("Priority Encoding Map:", dict(zip(le.classes_, le.transform(le.classes_))))

# Define Features (X) and Target (y)
X = df.drop(['diagnosis', 'priority', 'priority_encoded'], axis=1)
y = df['priority_encoded']

# Split data: 70% Train, 30% Test. Stratify ensures class balance in both sets.
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y 
)

# Feature Scaling: Use StandardScaler to normalize feature ranges
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train_raw)
X_test = scaler.transform(X_test_raw)
print(f"Data Split: Training set {X_train.shape}, Test set {X_test.shape}")


# --- 4. Goal 2: Model Training ---
print("\n--- Training Random Forest Model ---")

# Initialize and train the classifier. 'balanced' helps manage potential class imbalance.
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced') 
rf_model.fit(X_train, y_train)
print("Random Forest model training complete.")

# Make predictions on the held-out test data
y_pred = rf_model.predict(X_test)


# --- 5. Goal 3: Model Evaluation (Metrics) ---
print("\n--- Model Performance Evaluation ---")

# Calculate required metrics
accuracy = accuracy_score(y_test, y_pred)
f1_weighted = f1_score(y_test, y_pred, average='weighted')

print("--- REQUIRED PERFORMANCE METRICS ---")
print(f"1. Accuracy Score: {accuracy:.4f}")
print(f"2. F1-Score (Weighted): {f1_weighted:.4f}")

# Detailed breakdown is crucial for multi-class problems
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))


# --- 6. BONUS: Feature Importance Analysis (For better resource justification) ---
print("\n--- Feature Importance for Model Interpretation ---")

# Extract importances and map them back to the original feature names
importances = rf_model.feature_importances_
feature_importances = pd.Series(importances, index=X_train_raw.columns).sort_values(ascending=False)

print("Top 10 Features Driving Priority Prediction:")
print("-" * 40)
print(feature_importances.head(10))

# Optional: Visualize the top 10 features
plt.figure(figsize=(10, 6))
feature_importances.head(10).plot(kind='barh', color='skyblue')
plt.title('Top 10 Feature Importances for Resource Allocation Priority')
plt.xlabel('Importance Score (Gini/Mean Decrease Impurity)')
plt.ylabel('Feature Name')
plt.gca().invert_yaxis() # Highest importance at the top
plt.tight_layout()
plt.show()