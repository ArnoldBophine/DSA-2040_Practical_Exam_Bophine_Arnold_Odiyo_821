import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import MinMaxScaler
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def perform_clustering():
    print("--- 2. Data Clustering ---")
    
    # Load and Normalize Data (Re-using logic, or import if module structure allowed, ensuring standalone execution here)
    iris = load_iris()
    X = iris.data
    y_true = iris.target
    feature_names = iris.feature_names
    
    # Normalize for Clustering
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 2.1 K-Means with k=3
    print("\nRunning K-Means (k=3)...")
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    y_pred = kmeans.fit_predict(X_scaled)
    
    # Calculate ARI
    ari = adjusted_rand_score(y_true, y_pred)
    print(f"Adjusted Rand Index (ARI): {ari:.4f}")
    
    # 2.2 Experimentation (Elbow Method)
    print("\nGenerating Elbow Curve...")
    inertia = []
    k_values = range(2, 11)
    
    for k in k_values:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertia.append(km.inertia_)
        
    # Plot Elbow Curve
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, inertia, marker='o')
    plt.title('Elbow Method for Optimal k')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, 'elbow_curve.png'))
    plt.close()
    print("Elbow curve saved to elbow_curve.png")
    
    # 2.3 Visualization (Scatter Plot)
    print("\nVisualizing Clusters...")
    # Using Petal Length (index 2) vs Petal Width (index 3)
    plt.figure(figsize=(10, 6))
    
    # Create DataFrame for plotting
    df_plot = pd.DataFrame(X_scaled, columns=feature_names)
    df_plot['Cluster'] = y_pred
    
    sns.scatterplot(
        data=df_plot, 
        x=feature_names[2], 
        y=feature_names[3], 
        hue='Cluster', 
        palette='viridis',
        s=100,
        alpha=0.7
    )
    
    # Plot Centroids
    centroids = kmeans.cluster_centers_
    plt.scatter(
        centroids[:, 2], 
        centroids[:, 3], 
        c='red', 
        s=200, 
        marker='X', 
        label='Centroids'
    )
    
    plt.title('K-Means Clusters (Petal Length vs Width)')
    plt.legend()
    plt.savefig(os.path.join(BASE_DIR, 'clusters_scatter.png'))
    plt.close()
    print("Cluster visualization saved to clusters_scatter.png")
    
    return ari

if __name__ == "__main__":
    perform_clustering()
