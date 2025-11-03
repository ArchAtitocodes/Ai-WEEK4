# Predictive Analytics for Resource Allocation

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Libraries](https://img.shields.io/badge/libraries-pandas%2C%20scikit--learn%2C%20matplotlib-orange)
![Status](https://img.shields.io/badge/status-complete-green)

## 📋 Project Overview

This project demonstrates the use of a machine learning model to predict resource allocation priority for medical cases. Using the Wisconsin Diagnostic Breast Cancer (WDBC) dataset, it builds a **Random Forest Classifier** to categorize cases into **High, Medium, or Low** priority levels.

The primary goal is to transform a binary classification problem (Malignant/Benign) into a more practical, multi-class resource allocation system. This allows for more nuanced decision-making, where resources can be triaged and assigned based on the predicted urgency of a case.

## ✨ Key Features

*   **Data Preprocessing**: Cleans the dataset and engineers a new multi-class target variable named `priority`.
*   **Feature Engineering**: Converts the binary 'diagnosis' (Malignant/Benign) into three priority levels based on diagnosis and tumor size (`radius_mean`).
*   **Model Training**: Implements a `RandomForestClassifier` from `scikit-learn`, a powerful ensemble model suitable for this classification task.
*   **Model Evaluation**: Measures model performance using key metrics like **Accuracy** and **Weighted F1-Score**.
*   **Feature Importance Analysis**: Identifies and visualizes the top 10 most influential features that the model uses to make its predictions, providing valuable insights for clinical interpretation.

## ⚙️ Project Structure

The project consists of the following files:

```
.
├── Task3_Resource_Allocation_Prediction.py  # Main Python script for the analysis
├── requirements.txt                         # List of Python dependencies
├── wdbc_data.csv                            # The dataset file (must be provided)
└── README.md                                # This documentation file
```

## 🛠️ Setup and Installation

To run this project, you need Python 3 and the libraries listed in `requirements.txt`.

1.  **Clone the Repository (or download the files)**:
    Make sure all files are in the same directory.

2.  **Get the Dataset**:
    You must have the dataset file named `wdbc_data.csv` in the same directory as the script. This file is not included in the repository. It can be downloaded from sources like the UCI Machine Learning Repository.

3.  **Install Dependencies**:
    Open your terminal or command prompt and run the following command to install the necessary Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ How to Run

Once the setup is complete, you can execute the script directly from your terminal:

```bash
python Task3_Resource_Allocation_Prediction.py
```

The script will perform all steps automatically and print the output to the console.

### Expected Output

The script will produce the following:
1.  Confirmation messages for library import and data loading.
2.  The calculated median radius used to split benign cases.
3.  The distribution of the new `priority` classes (High, Medium, Low).
4.  Confirmation of model training.
5.  A performance report including:
    *   **Accuracy Score**
    *   **Weighted F1-Score**
    *   A detailed **Classification Report** with precision, recall, and f1-score for each class.
6.  A list of the **Top 10 Features** that most heavily influence the model's predictions.
7.  A pop-up window displaying a bar chart that visualizes the feature importances.

**Example Console Output:**
```
Libraries imported successfully.
Dataset loaded. Initial shape: (569, 33)
Calculated Benign Split Threshold (radius_mean): 12.3400
...
--- Model Performance Evaluation ---
--- REQUIRED PERFORMANCE METRICS ---
1. Accuracy Score: 0.9708
2. F1-Score (Weighted): 0.9707

Detailed Classification Report:
              precision    recall  f1-score   support
        High       0.98      0.95      0.97        64
         Low       0.96      0.99      0.97        89
      Medium       1.00      0.94      0.97        18
...
--- Feature Importance for Model Interpretation ---
Top 10 Features Driving Priority Prediction:
----------------------------------------
concave points_worst    0.141585
perimeter_worst         0.121899
radius_worst            0.111955
...
```

## 🧠 Methodology

### 1. Feature Engineering

The core of this project is the creation of the `priority` target variable. The logic is as follows:
*   All **Malignant ('M')** cases are immediately assigned **'High'** priority.
*   **Benign ('B')** cases are further divided:
    *   Those with a `radius_mean` greater than or equal to the median radius of all benign tumors are assigned **'Medium'** priority.
    *   Those with a `radius_mean` below the median are assigned **'Low'** priority.

This creates a more granular target that is better suited for resource allocation than a simple binary diagnosis.

### 2. Model and Training

A **Random Forest Classifier** with 100 estimators is used. This model is an excellent choice as it is robust, handles non-linear relationships well, and provides feature importance scores out-of-the-box. The data is split into a 70% training set and a 30% testing set, with stratification to ensure that the class distribution is preserved in both sets. Features are scaled using `StandardScaler` to improve model performance.

---
