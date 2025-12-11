# DSA 2040 Practical Exam: Section 2 - Data Mining Report

**Student Name:** Arnold Bophine Odiyo  
**Student ID:** 821  
**Date:** December 11, 2025  

---

## Task 1: Data Preprocessing and Exploration

### 1.1 Methodology
The **Iris dataset** (150 samples, 4 features) was loaded and processed. 
- **Missing Values**: None found.
- **Normalization**: Features were scaled to [0, 1] range using `MinMaxScaler` to ensure distance-based algorithms (like K-Means and KNN) perform optimally.
- **Split**: Data was split 80% Training / 20% Testing.

### 1.2 Exploratory Data Analysis (EDA)
- **Pairplot Results**: Clear separation was observed between *Setosa* and the other two species based on Petal Length and Width. *Versicolor* and *Virginica* show some overlap.
- **Correlation**: `petal length` and `petal width` are highly correlated (0.96), suggesting redundancy, but also strong predictive power.

![Correlation Heatmap](correlation_heatmap.png)

---

## Task 2: Clustering Analysis

### 2.1 K-Means Implementation
K-Means clustering was applied with $k=3$ (corresponding to the 3 actual species). 
- **Adjusted Rand Index (ARI)**: The model achieved an ARI of **0.62**, indicating a reasonable match with ground truth labels but highlighting some misclassifications where species overlap (specifically *Versicolor* vs *Virginica*).

### 2.2 Optimal Number of Clusters
The **Elbow Method** was used to verify the optimal $k$. As seen in the curve below, the "elbow" bends distinctly at $k=3$, confirming that 3 natural clusters exist in the data.

![Elbow Curve](elbow_curve.png)

### 2.3 Cluster Visualization & Analysis
The scatter plot of Petal Length vs. Petal Width shows three distinct clusters.

![Cluster Scatter](clusters_scatter.png)

**Analysis:**
The clustering algorithm successfully identified the *Setosa* species (Cluster 0/Blue in my run) with 100% accuracy due to its linear separability. However, the boundary between *Versicolor* and *Virginica* is fuzzy. K-Means assumes spherical clusters, but the data distribution for these two species is somewhat elongated and overlapping, leading to some points being assigned to the wrong cluster.

**Real-World Application:**
In a business context, this technique is analogous to **Customer Segmentation**. Just as we grouped flowers by physical traits, a retailer could group customers by *Recency* and *Frequency* of purchase. Misclassification here (e.g., treating a high-value customer as mid-tier) carries a cost, similar to scientific taxonomy errors. The clear separation of "Cluster 0" suggests a segment of low-hanging fruit (easy to identify), while the overlap in others suggests a need for more features (or complex models) to distinguish subtle differences between mid-tier and premium segments.

---

## Task 3: Classification and Association Rule Mining

### 3.1 Classification: Decision Tree vs. KNN

Two models were trained on the preprocessed Iris data.

**Results (Test Set):**
- **Decision Tree Accuracy**: 1.00 (100%)
- **KNN (k=5) Accuracy**: 1.00 (100%)

**Cross-Validation (5-Fold) - More Robust Estimate:**
- **Decision Tree**: ~95.3%
- **KNN**: ~97.3%

**Comparison:**
While both models achieved perfect accuracy on the small test set, Cross-Validation suggests **KNN is slightly more robust** (97.3% vs 95.3%). Decision Trees are prone to overfitting (high variance), creating complex boundaries for specific training points. KNN's distance-based averaging often generalizes better on smooth data manifolds like Iris. However, the Decision Tree (visualized below) offers superior interpretability—we can see exactly which "rules" (e.g., `petal width <= 0.8`) define a species.

![Decision Tree](decision_tree.png)

### 3.2 Association Rule Mining (Market Basket Analysis)
Synthetic transaction data (50 baskets) was generated with injected patterns (e.g., Bread and Butter).

**Algorithm**: Apriori
**Parameters**: Min Support = 0.2, Min Confidence = 0.5.

**Top Rule Discovered:**
*   **Rule**: `Bread -> Butter` (or inverse)
*   **Support**: ~0.36 (Occurs in 36% of all transactions)
*   **Confidence**: ~0.69 (If Bread is bought, there is a 69% chance Butter is also bought)
*   **Lift**: ~1.33

**Implications:**
A Lift > 1.0 indicates a positive correlation. A lift of 1.33 means customers are **1.33 times more likely** to buy Butter if they are already buying Bread compared to the average customer. 
*   **Retail Strategy**: Place Bread and Butter near each other to increase convenience, or place them far apart to force traversal through the store (exposing customers to other items). Alternatively, offer a "Breakfast Bundle" discount to drive volume.
