import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def preprocess_iris():
    print("--- 1.1 Load and Preprocess Iris Dataset ---")
    
    # 1. Load Data
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    df['species'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
    
    print("\nData Sample (First 5 rows):")
    print(df.head())
    
    # 2. Handle Missing Values
    print("\nChecking for missing values:")
    print(df.isnull().sum())
    # No missing values in standard Iris, but good to check
    
    # 3. Normalize Features (Min-Max Scaling)
    print("\nNormalizing features (Min-Max Split)...")
    scaler = MinMaxScaler()
    feature_cols = iris.feature_names
    df_normalized = df.copy()
    df_normalized[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    print("Normalized Data Sample:")
    print(df_normalized.head())
    
    return df, df_normalized, feature_cols

def perform_eda(df, feature_cols):
    print("\n--- 1.3 Exploratory Data Analysis (EDA) ---")
    
    # 1. Summary Statistics
    print("\nSummary Statistics:")
    print(df.describe())
    
    # 2. Pairplot
    print("Generating Pairplot...")
    sns.pairplot(df, hue='species', diag_kind='hist')
    plt.savefig(os.path.join(BASE_DIR, 'pairplot.png'))
    plt.close()
    
    # 3. Correlation Heatmap
    print("Generating Correlation Heatmap...")
    plt.figure(figsize=(10, 8))
    corr = df[feature_cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Iris Features')
    plt.savefig(os.path.join(BASE_DIR, 'correlation_heatmap.png'))
    plt.close()
    
    # 4. Outlier Detection (Boxplots)
    print("Generating Boxplots for Outlier Detection...")
    plt.figure(figsize=(12, 6))
    df_melted = pd.melt(df, id_vars=['species'], value_vars=feature_cols)
    sns.boxplot(x='variable', y='value', data=df_melted)
    plt.title('Boxplot of Iris Features')
    plt.savefig(os.path.join(BASE_DIR, 'boxplots.png'))
    plt.close()
    
    print("EDA Visualizations saved.")

def split_data(df, feature_cols):
    print("\n--- 1.4 Train-Test Split ---")
    X = df[feature_cols]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Train Set Shape: {X_train.shape}")
    print(f"Test Set Shape: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # 1. Preprocess
    df_original, df_norm, features = preprocess_iris()
    
    # 2. EDA (on original scale data usually better for interpretation, or normalized? instructions say normalize then EDA? 
    # Usually EDA is on raw data for distribution, but boxplots for outliers helps on either. 
    # Let's do EDA on original data for clearer interpretation of values)
    perform_eda(df_original, features)
    
    # 3. Split (using normalized data for ML? Instructions don't strictly say, but usually yes for distance based algos like KNN/KMeans)
    # Task 1.4 just says "Create split function". Later tasks use it.
    # We'll split the normalized data as it's better for future steps (KMeans, KNN).
    split_data(df_norm, features)
    
    print("\nPreprocessing Task Completed.")
