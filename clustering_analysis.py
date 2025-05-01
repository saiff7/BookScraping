import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def run_clustering_analysis():
    """Perform clustering analysis to group books by price"""
    # Connect to the database
    conn = sqlite3.connect('books.db')
    
    # Load data into a pandas DataFrame
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    
    print("=== CLUSTERING ANALYSIS: GROUPING BOOKS BY PRICE ===")
    print(f"Analyzing {len(books_df)} books to identify price categories\n")
    
    # Extract price as feature for clustering
    X = books_df[['price']].values
    
    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Determine optimal number of clusters using silhouette score
    # Try 2-6 clusters
    silhouette_scores = []
    K_range = range(2, 7)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        
        if len(np.unique(kmeans.labels_)) > 1:  # Check if there's more than one cluster
            score = silhouette_score(X_scaled, kmeans.labels_)
            silhouette_scores.append(score)
            print(f"Silhouette score for k={k}: {score:.4f}")
        else:
            silhouette_scores.append(-1)
            print(f"Only one cluster formed for k={k}, silhouette score not available")
    
    # Find the optimal k with highest silhouette score
    optimal_k = K_range[np.argmax(silhouette_scores)]
    print(f"\nOptimal number of clusters: {optimal_k}")
    
    # Plot silhouette scores
    plt.figure(figsize=(10, 6))
    plt.plot(K_range, silhouette_scores, 'bo-')
    plt.title('Silhouette Score Method For Optimal k')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette Score')
    plt.grid(True)
    plt.savefig('silhouette_scores.png', dpi=300, bbox_inches='tight')
    
    # Apply KMeans with optimal k
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    # Add cluster labels to the DataFrame
    books_df['cluster'] = kmeans.labels_
    
    # Get cluster centers and transform back to original scale
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    
    # Sort clusters by price (center value)
    cluster_order = np.argsort(centers.flatten())
    
    # Map cluster numbers to meaningful labels based on price ranges
    price_labels = ["Low Price", "Medium Price", "High Price"]
    if optimal_k <= 3:
        label_mapping = {cluster_order[i]: price_labels[i] for i in range(optimal_k)}
    else:
        # For more than 3 clusters, use numbered price categories
        label_mapping = {cluster_order[i]: f"Price Category {i+1}" for i in range(optimal_k)}
    
    books_df['price_category'] = books_df['cluster'].map(label_mapping)
    
    # Display cluster information
    print("\nCluster Centers (Average Price):")
    for i, center in enumerate(centers):
        label = label_mapping[i]
        print(f"Cluster {i} ({label}): £{center[0]:.2f}")
    
    print("\nCluster Sizes:")
    cluster_counts = books_df['price_category'].value_counts()
    for category, count in cluster_counts.items():
        print(f"{category}: {count} books ({count/len(books_df)*100:.1f}%)")
    
    # Calculate statistics for each cluster
    cluster_stats = books_df.groupby('price_category').agg({
        'price': ['min', 'max', 'mean', 'std', 'count']
    })
    
    print("\nPrice Range for Each Category:")
    for category in cluster_stats.index:
        min_price = cluster_stats.loc[category, ('price', 'min')]
        max_price = cluster_stats.loc[category, ('price', 'max')]
        mean_price = cluster_stats.loc[category, ('price', 'mean')]
        std_price = cluster_stats.loc[category, ('price', 'std')]
        count = cluster_stats.loc[category, ('price', 'count')]
        
        print(f"{category}: £{min_price:.2f} - £{max_price:.2f} (Avg: £{mean_price:.2f}, Std: £{std_price:.2f}, Count: {count})")
    
    # Create visualizations
    
    # 1. Scatter plot with cluster colors
    plt.figure(figsize=(12, 8))
    
    # Add jitter for better visualization
    books_df['rating_jitter'] = books_df['rating'] + np.random.normal(0, 0.1, size=len(books_df))
    
    # Create scatter plot
    sns.scatterplot(x='rating_jitter', y='price', hue='price_category', data=books_df, 
                   palette='viridis', alpha=0.7, s=80)
    
    # Add cluster centers
    for i, center in enumerate(centers):
        label = label_mapping[i]
        plt.scatter(3, center[0], s=200, c='red', marker='X', edgecolor='black', label=f"Center: {label}")
    
    plt.title('Book Clusters by Price and Rating')
    plt.xlabel('Rating')
    plt.ylabel('Price (£)')
    plt.xticks([1, 2, 3, 4, 5])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Price Category')
    plt.savefig('price_clusters.png', dpi=300, bbox_inches='tight')
    
    # 2. Box plot of price by cluster
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='price_category', y='price', data=books_df, palette='viridis', order=cluster_counts.index)
    plt.title('Price Distribution by Cluster')
    plt.xlabel('Price Category')
    plt.ylabel('Price (£)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('cluster_boxplot.png', dpi=300, bbox_inches='tight')
    
    # 3. Rating distribution by cluster
    plt.figure(figsize=(12, 8))
    for category in cluster_counts.index:
        subset = books_df[books_df['price_category'] == category]
        rating_dist = subset['rating'].value_counts(normalize=True).sort_index() * 100
        plt.plot(rating_dist.index, rating_dist.values, 'o-', linewidth=2, label=category)
    
    plt.title('Rating Distribution by Price Category')
    plt.xlabel('Rating')
    plt.ylabel('Percentage of Books (%)')
    plt.xticks([1, 2, 3, 4, 5])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Price Category')
    plt.savefig('rating_by_cluster.png', dpi=300, bbox_inches='tight')
    
    # Sample books from each cluster
    print("\nSample Books from Each Price Category:")
    for category in cluster_counts.index:
        sample = books_df[books_df['price_category'] == category].sample(min(5, len(books_df[books_df['price_category'] == category])))
        print(f"\n{category} (sample of {min(5, len(books_df[books_df['price_category'] == category]))} books):")
        for _, book in sample.iterrows():
            print(f"- {book['title']} (£{book['price']:.2f}, Rating: {book['rating']})")
    
    print("\nClustering analysis complete. Visualizations saved as PNG files.")
    conn.close()

if __name__ == "__main__":
    run_clustering_analysis()