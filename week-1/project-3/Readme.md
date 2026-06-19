# Diabetes Prediction Analysis

## 📋 Overview

This project involves developing a machine learning model to predict whether patients have diabetes based on diagnostic measurements. The analysis includes comprehensive data preprocessing, exploratory data analysis, and implementation of multiple classification algorithms to identify the best-performing model.

## 📊 Dataset

The dataset contains **768 samples** with the following features:

| Feature | Description |
|---------|-------------|
| **Pregnancies** | Number of times patient has been pregnant |
| **Glucose** | Plasma glucose concentration (2 hours after oral glucose test) - **0 = missing data** |
| **BloodPressure** | Diastolic blood pressure (mm Hg) - **0 = missing data** |
| **SkinThickness** | Triceps skin fold thickness (mm) - **0 = missing data** |
| **Insulin** | 2-Hour serum insulin level (mu U/ml) - **0 = missing data** |
| **BMI** | Body mass index (kg/m²) - **0 = missing data** |
| **DiabetesPedigreeFunction** | Genetic risk score based on family history |
| **Age** | Patient's age in years |
| **Outcome** | Target variable (0 = No Diabetes, 1 = Diabetes) |

## 🎯 Objective

Build a classification model that predicts diabetes diagnosis with high accuracy and F1-score.

## 🔍 Exploratory Data Analysis

### Key Findings:

1. **Missing Values**: Several features use 0 as a placeholder for missing data:
   - Glucose: ~0.65% missing
   - BloodPressure: ~4.77% missing
   - SkinThickness: ~42% missing (highest)
   - BMI: ~1.45% missing

2. **Feature Distributions**:
   - Normally distributed: Glucose, BloodPressure, SkinThickness, BMI
   - Right-skewed: DiabetesPedigreeFunction, Age

3. **Outliers**: Insulin feature shows significant outliers

4. **Class Imbalance**: Dataset is imbalanced with more non-diabetic cases

5. **Correlations**: Highest correlation between Age and Pregnancies (54%)

## 🛠️ Data Preprocessing

### Missing Value Handling
- **Mean Imputation**: Used for Glucose, BloodPressure, and BMI
- **KNN Imputation**: Used for SkinThickness (42% missing)

### Outlier Treatment
- **RobustScaler**: Applied to handle outliers effectively

### Class Imbalance
- **SMOTE (Synthetic Minority Over-sampling Technique)**: Used to balance the dataset

### Train-Test Split
- 90% training, 10% testing with random seed 231 for reproducibility

## 🤖 Models Implemented

### Algorithms Tested:
1. **Logistic Regression**
2. **Random Forest Classifier**
3. **Support Vector Classifier (SVC)**
4. **K-Nearest Neighbors (KNN)**
5. **Decision Tree Classifier**

Each model was evaluated with and without **GridSearchCV** hyperparameter tuning.

## 📈 Model Performance

| Model | Accuracy | F1-Score |
|-------|----------|----------|
| KNN with GridSearch | **77.92%** | **65.31%** |
| Logistic Regression | 77.92% | 63.83% |
| SVC | 76.62% | 62.50% |
| KNN (default) | 75.32% | 59.57% |
| Logistic Regression (GridSearch) | 75.32% | 57.78% |
| Random Forest | 74.03% | 56.52% |
| Decision Tree (GridSearch) | 67.53% | 56.14% |
| Decision Tree | 72.73% | 55.32% |
| SVC (GridSearch) | 72.73% | 55.32% |
| Random Forest (GridSearch) | 74.03% | 56.52% |

### Best Model: KNN with GridSearch
- **F1-Score**: 65.31%
- **Accuracy**: 77.92%

## 🚀 Pipeline Implementation

A complete preprocessing and modeling pipeline was created using `sklearn.pipeline.Pipeline`:

1. **Preprocessor**: ColumnTransformer with:
   - Mean imputation for missing values
   - KNN imputation for SkinThickness
   - Passthrough for remaining features

2. **Scaler**: RobustScaler for outlier-resistant scaling

3. **Classifier**: K-Nearest Neighbors with optimized parameters:
   - `n_neighbors=11`
   - `weights='distance'`
   - `metric='manhattan'`
   - `p=1`

## 💾 Model Persistence

The final model pipeline is saved using **joblib**:

```python
MODEL_NAME = "diabet-analysis.joblib"
joblib.dump(pipeline, MODEL_NAME)
```

### Loading and Testing:
```python
pipline_loaded = joblib.load(MODEL_NAME)
```

## 📊 Evaluation Metrics Used

- **Accuracy**: Overall correct predictions
- **F1-Score**: Harmonic mean of precision and recall (primary metric)
- **Confusion Matrix**: Visual representation of predictions
- **ROC Curve**: Area Under the Curve (AUC) analysis

## 🔧 Requirements

### Libraries Used:
- pandas, numpy (data manipulation)
- matplotlib, seaborn (visualization)
- scikit-learn (machine learning)
- imbalanced-learn (SMOTE)
- joblib (model serialization)

### Key Modules:
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
```

## 📝 Key Insights

1. **Data Quality**: Careful handling of missing values (especially 0 values) is crucial
2. **Feature Engineering**: Proper scaling and outlier treatment improves model performance
3. **Class Imbalance**: Addressing imbalance significantly improves F1-score
4. **Model Selection**: KNN with GridSearchCV outperformed other algorithms
5. **Pipeline Benefits**: Pipeline ensures reproducibility and prevents data leakage

## 🎓 Lessons Learned

- Always investigate the meaning of zero values in medical datasets
- Use appropriate imputation strategies (KNN for high missing rates)
- Handle class imbalance for improved minority class prediction
- GridSearchCV helps find optimal hyperparameters
- Pipeline ensures consistent preprocessing across training and test data
