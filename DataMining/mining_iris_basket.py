import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from mlxtend.frequent_patterns import apriori, association_rules
import random
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def classification_task():
    print("--- 3.1 Classification (Iris) ---")
    
    # Load Data
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    class_names = iris.target_names
    
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3.1.1 Decision Tree
    print("\nTraining Decision Tree...")
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    
    print("Decision Tree Metrics:")
    print(classification_report(y_test, y_pred_dt, target_names=class_names))
    
    # Visualize Tree
    plt.figure(figsize=(12, 8))
    plot_tree(dt, filled=True, feature_names=feature_names, class_names=class_names)
    plt.title("Decision Tree Visualization")
    plt.savefig(os.path.join(BASE_DIR, 'decision_tree.png'))
    plt.close()
    print("Decision Tree plot saved to decision_tree.png")
    
    # 3.1.2 KNN
    print("\nTraining KNN (k=5)...")
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    y_pred_knn = knn.predict(X_test)
    
    print("KNN Metrics:")
    print(classification_report(y_test, y_pred_knn, target_names=class_names))
    
    # Compare Scores
    acc_dt = accuracy_score(y_test, y_pred_dt)
    acc_knn = accuracy_score(y_test, y_pred_knn)
    print(f"\nComparison (Test Set): DT Accuracy={acc_dt:.4f} vs KNN Accuracy={acc_knn:.4f}")
    
    # Cross-Validation (to address 100% "too good to be true" concern)
    from sklearn.model_selection import cross_val_score
    print("\n--- Cross-Validation (5-Fold) ---")
    cv_dt = cross_val_score(dt, X, y, cv=5)
    cv_knn = cross_val_score(knn, X, y, cv=5)
    
    print(f"Decision Tree CV Accuracy: {cv_dt.mean():.4f} (+/- {cv_dt.std() * 2:.4f})")
    print(f"KNN CV Accuracy:           {cv_knn.mean():.4f} (+/- {cv_knn.std() * 2:.4f})")

    return acc_dt, acc_knn

def association_rule_mining():
    print("\n--- 3.2 Association Rule Mining (Market Basket) ---")
    
    # 3.2.1 Generate Synthetic Transactions
    print("Generating Synthetic Transaction Data...")
    items = ['Milk', 'Bread', 'Butter', 'Eggs', 'Cheese', 'Yogurt', 'Apple', 'Banana', 'Coffee', 'Tea']
    
    # Seed for reproducibility
    random.seed(42)
    
    transactions = []
    num_transactions = 50
    
    for _ in range(num_transactions):
        # Create random basket size 3-6 items
        basket_size = random.randint(3, 6)
        basket = random.sample(items, basket_size)
        
        # Inject patterns (e.g., Bread + Butter often together)
        if 'Bread' in basket and 'Butter' not in basket:
            if random.random() > 0.3: # 70% chance to add butter if bread is there
                basket[-1] = 'Butter' # Replace last item
        
        transactions.append(basket)
        
    print(f"Generated {len(transactions)} transactions.")
    print("Sample Transaction:", transactions[0])
    
    # Preprocess for Apriori (One-Hot Encoding)
    # Using mlxtend's TransactionEncoder is standard, but manual way for clarity if package missing? 
    # Let's assume mlxtend is available (Standard for this task).
    try:
        from mlxtend.preprocessing import TransactionEncoder
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_trans = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 3.2.2 Apriori
        print("\nRunning Apriori (Min Support=0.2)...")
        frequent_itemsets = apriori(df_trans, min_support=0.2, use_colnames=True)
        print(f"Found {len(frequent_itemsets)} frequent itemsets.")
        
        # 3.2.3 Association Rules
        print("\nExtracting Rules (Min Confidence=0.5)...")
        if not frequent_itemsets.empty:
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
            
            # Sort by Lift
            rules = rules.sort_values('lift', ascending=False)
            
            print("\nTop 5 Association Rules:")
            print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(5))
            
            # Save rules
            rules.to_csv(os.path.join(BASE_DIR, 'association_rules.csv'), index=False)
            print("Rules saved to association_rules.csv")
            return len(rules)
        else:
            print("No frequent itemsets found with current support threshold.")
            return 0
            
    except ImportError:
        print("Error: mlxtend library not found. Please pip install mlxtend.")
        return 0

if __name__ == "__main__":
    classification_task()
    association_rule_mining()
