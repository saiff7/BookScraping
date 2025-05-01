import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_descriptive_analysis():
    """Perform descriptive analysis on the book data"""
    # Connect to the database
    conn = sqlite3.connect('books.db')
    
    # Load data into a pandas DataFrame
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    
    # Display basic statistics
    print("=== DATASET OVERVIEW ===")
    print(f"Total number of books: {len(books_df)}")
    print("\n=== PRICE STATISTICS ===")
    print(f"Average price: £{books_df['price'].mean():.2f}")
    print(f"Minimum price: £{books_df['price'].min():.2f}")
    print(f"Maximum price: £{books_df['price'].max():.2f}")
    print(f"Median price: £{books_df['price'].median():.2f}")
    print(f"Standard deviation: £{books_df['price'].std():.2f}")
    
    print("\n=== RATING DISTRIBUTION ===")
    rating_counts = books_df['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"Rating {rating}: {count} books ({count/len(books_df)*100:.1f}%)")
    
    print("\n=== AVAILABILITY STATISTICS ===")
    print(f"Average availability: {books_df['availability'].mean():.2f} books")
    print(f"Maximum availability: {books_df['availability'].max()} books")
    
    # Top 10 cheapest books
    print("\n=== TOP 10 CHEAPEST BOOKS ===")
    cheapest_books = books_df.sort_values('price').head(10)
    for idx, row in cheapest_books.iterrows():
        print(f"{row['title']} - £{row['price']:.2f}")
    
    # Top 10 most expensive books
    print("\n=== TOP 10 MOST EXPENSIVE BOOKS ===")
    expensive_books = books_df.sort_values('price', ascending=False).head(10)
    for idx, row in expensive_books.iterrows():
        print(f"{row['title']} - £{row['price']:.2f}")
    
    # Create visualizations
    sns.set_style("whitegrid")
    
    # Histogram of book prices
    plt.figure(figsize=(12, 6))
    sns.histplot(books_df['price'], bins=20, kde=True)
    plt.title('Distribution of Book Prices')
    plt.xlabel('Price (£)')
    plt.ylabel('Number of Books')
    plt.savefig('price_distribution.png', dpi=300, bbox_inches='tight')
    
    # Bar chart of top 10 most expensive books
    plt.figure(figsize=(14, 8))
    chart = sns.barplot(x='price', y='title', data=expensive_books, palette='viridis')
    plt.title('Top 10 Most Expensive Books')
    plt.xlabel('Price (£)')
    plt.tight_layout()
    plt.savefig('top_expensive_books.png', dpi=300, bbox_inches='tight')
    
    # Bar chart of top 10 cheapest books
    plt.figure(figsize=(14, 8))
    chart = sns.barplot(x='price', y='title', data=cheapest_books, palette='viridis')
    plt.title('Top 10 Cheapest Books')
    plt.xlabel('Price (£)')
    plt.tight_layout()
    plt.savefig('top_cheapest_books.png', dpi=300, bbox_inches='tight')
    
    # Distribution of ratings
    plt.figure(figsize=(10, 6))
    sns.countplot(x='rating', data=books_df, palette='viridis')
    plt.title('Distribution of Book Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Number of Books')
    plt.savefig('rating_distribution.png', dpi=300, bbox_inches='tight')
    
    # Boxplot of prices by rating
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='rating', y='price', data=books_df, palette='viridis')
    plt.title('Book Prices by Rating')
    plt.xlabel('Rating')
    plt.ylabel('Price (£)')
    plt.savefig('price_by_rating.png', dpi=300, bbox_inches='tight')
    
    print("\nDescriptive analysis complete. Visualizations saved as PNG files.")
    conn.close()

if __name__ == "__main__":
    run_descriptive_analysis()