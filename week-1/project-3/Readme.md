# 🩺 Diabetes Prediction Project

## 📋 Project Overview

This project develops machine learning models to predict diabetes onset using the Pima Indians Diabetes Database. The goal is to accurately classify patients based on diagnostic measurements while handling missing data, class imbalance, and outliers.

**Dataset**: 768 samples with 8 features + target (`Outcome`).  
**Task**: Binary classification (diabetes: 1, no diabetes: 0).  
**Metrics**: Accuracy and F1-score (as requested by the team).

---

## 🏆 Best Performing Model

The **Support Vector Classifier (SVC)** with default parameters (after scaling and SMOTE) achieved the highest F1-score with competitive accuracy:

| Metric       | Score |
|--------------|-------|
| **F1-score** | **65.55%** |
| Accuracy     | 73.38% |

But SVC currently dose not work with pipeline, I chosed KNN (with GridSearch) which has best scores after SVC:

| Metric       | Score |
|--------------|-------|
| **F1-score** | **65.57%** |
| Accuracy     | 72.73% |

---

## 📊 Model Performance Comparison

| Model | F1‑Score | Accuracy |
|-------|----------|----------|
| **SVC (default)** | **65.55%** | **73.38%** |
| KNN (GridSearch)  | 65.57%   | 72.73%   |
| Random Forest (GridSearch) | 63.64% | 74.03% |
| Logistic Regression (GridSearch) | 63.16% | 72.73% |
| Decision Tree | 60.61% | 66.23% |

> **Note**: GridSearchCV was used for hyperparameter tuning; SVC with default parameters (`C=1`, `kernel='rbf'`, `gamma='scale'`) outperformed its tuned version (which had lower F1).

---

## 🔧 Data Preprocessing

1. **Handling Missing Values**  
   - Columns with `0` as missing: `Glucose`, `BloodPressure`, `SkinThickness`, `BMI`.  
   - **Mean imputation** for `Glucose`, `BloodPressure`, `BMI`.  
   - **KNN imputation** for `SkinThickness` (due to high missing rate ~42%).

2. **Outlier Treatment**  
   - Applied **RobustScaler** to reduce outlier influence.

3. **Class Imbalance**  
   - Used **SMOTE** (Synthetic Minority Oversampling) to balance the training set.

4. **Feature Engineering**  
   - Created an interaction feature `Glucose_BMI = Glucose × BMI`, though it did not improve performance.

---

## 📈 Exploratory Data Analysis

- **Feature Importance** (Random Forest):  
  `Glucose` and `BMI` were the most influential features.
- **Correlation**: Highest correlation between `Age` and `Pregnancies` (0.54).
- **Missing Data**: `Insulin` had ~48% missing values, `SkinThickness` ~42%.
- **Class Distribution**: Imbalanced – ~65% negative, 35% positive.

---

## 🚀 Live Demo

Try the application directly:  
👉 [Diabetes Prediction Demo](https://huggingface.co/spaces/sirunchained/diabet-analysis)

---

## 📁 Repository Structure

```
├── main.ipynb          # Full pipeline: EDA, preprocessing, modeling, evaluation
├── diabetes.csv        # Dataset
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔧 Requirements

Key libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `imbalanced-learn`, `joblib`.

---

## 💻 Usage

1. Clone the repository.
2. Install dependencies.
3. Run `jupyter notebook main.ipynb` to explore the full analysis.
4. Or launch the Hugging Face Space for instant predictions.

---

## 📝 Notes

- The notebook includes detailed visualisations (histograms, box plots, correlation heatmap, ROC curves).
- SMOTE was applied **after** train/test split to avoid data leakage.
- All models were evaluated using cross‑validation and confusion matrices.

---

## 👨‍💻 Author

**SirUnchained**

---

*This project was developed as a solution for a diabetes prediction task, demonstrating a complete machine learning workflow.*