import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

def run_availability_analysis():
    """Analyze book availability in relation to price and rating"""
    # Connect to the database
    conn = sqlite3.connect('books.db')
    
    # Load data into a pandas DataFrame
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    
    print("=== AVAILABILITY ANALYSIS ===")
    print(f"Analyzing {len(books_df)} books to examine inventory patterns\n")
    
    # Calculate availability statistics
    print("Availability Statistics:")
    print(f"Average availability: {books_df['availability'].mean():.2f} books")
    print(f"Median availability: {books_df['availability'].median():.2f} books")
    print(f"Minimum availability: {books_df['availability'].min()} books")
    print(f"Maximum availability: {books_df['availability'].max()} books")
    print(f"Standard deviation: {books_df['availability'].std():.2f} books")
    
    # Find the books with highest stock available
    top_stock_books = books_df.sort_values('availability', ascending=False).head(15)
    
    print("\nTop 15 Books with Highest Stock Available:")
    for idx, row in top_stock_books.iterrows():
        print(f"{row['title']} - {row['availability']} in stock - £{row['price']:.2f} - Rating: {row['rating']}")
    
    # Check correlation between availability and price
    corr_price, p_value_price = pearsonr(books_df['availability'], books_df['price'])
    print(f"\nCorrelation between availability and price: {corr_price:.4f} (p-value: {p_value_price:.4f})")
    
    if p_value_price < 0.05:
        significance = "statistically significant"
    else:
        significance = "not statistically significant"
        
    print(f"The relationship between availability and price is {significance}.")
    
    if abs(corr_price) < 0.1:
        strength = "very weak"
    elif abs(corr_price) < 0.3:
        strength = "weak"
    elif abs(corr_price) < 0.5:
        strength = "moderate"
    else:
        strength = "strong"
        
    print(f"The correlation is {strength} and {corr_price > 0 and 'positive' or 'negative'}.")
    
    # Check correlation between availability and rating
    corr_rating, p_value_rating = pearsonr(books_df['availability'], books_df['rating'])
    print(f"\nCorrelation between availability and rating: {corr_rating:.4f} (p-value: {p_value_rating:.4f})")
    
    if p_value_rating < 0.05:
        significance = "statistically significant"
    else:
        significance = "not statistically significant"
        
    print(f"The relationship between availability and rating is {significance}.")
    
    if abs(corr_rating) < 0.1:
        strength = "very weak"
    elif abs(corr_rating) < 0.3:
        strength = "weak"
    elif abs(corr_rating) < 0.5:
        strength = "moderate"
    else:
        strength = "strong"
        
    print(f"The correlation is {strength} and {corr_rating > 0 and 'positive' or 'negative'}.")
    
    # Calculate average availability by rating
    avg_availability_by_rating = books_df.groupby('rating')['availability'].agg(['mean', 'median', 'count']).reset_index()
    avg_availability_by_rating.columns = ['Rating', 'Average Availability', 'Median Availability', 'Number of Books']
    avg_availability_by_rating['Average Availability'] = avg_availability_by_rating['Average Availability'].round(2)
    
    print("\nAverage Availability by Rating:")
    print(avg_availability_by_rating.to_string(index=False))
    
    # Create visualizations
    
    # 1. Scatter plot of availability vs price
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='price', y='availability', hue='rating', data=books_df, palette='viridis', s=80, alpha=0.7)
    plt.title('Book Availability vs Price (colored by Rating)')
    plt.xlabel('Price (£)')
    plt.ylabel('Availability (Number of Books in Stock)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Rating')
    
    # Add regression line
    sns.regplot(x='price', y='availability', data=books_df, scatter=False, color='red', line_kws={"linewidth": 2})
    
    plt.savefig('availability_vs_price.png', dpi=300, bbox_inches='tight')
    
    # 2. Boxplot of availability by rating
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='rating', y='availability', data=books_df, palette='viridis')
    plt.title('Book Availability by Rating')
    plt.xlabel('Rating')
    plt.ylabel('Availability (Number of Books in Stock)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('availability_by_rating.png', dpi=300, bbox_inches='tight')
    
    # 3. Histogram of availability
    plt.figure(figsize=(12, 6))
    sns.histplot(books_df['availability'], bins=20, kde=True)
    plt.title('Distribution of Book Availability')
    plt.xlabel('Availability (Number of Books in Stock)')
    plt.ylabel('Number of Books')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('availability_distribution.png', dpi=300, bbox_inches='tight')
    
    # Calculate availability statistics by price range
    books_df['price_range'] = pd.cut(books_df['price'], 
                                    bins=[0, 20, 40, 60, float('inf')], 
                                    labels=['£0-£20', '£20-£40', '£40-£60', '£60+'])
    
    avg_availability_by_price = books_df.groupby('price_range')['availability'].agg(['mean', 'median', 'count']).reset_index()
    avg_availability_by_price.columns = ['Price Range', 'Average Availability', 'Median Availability', 'Number of Books']
    avg_availability_by_price['Average Availability'] = avg_availability_by_price['Average Availability'].round(2)
    
    print("\nAverage Availability by Price Range:")
    print(avg_availability_by_price.to_string(index=False))
    
    # 4. Bar chart of average availability by price range
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Price Range', y='Average Availability', data=avg_availability_by_price, palette='viridis')
    plt.title('Average Book Availability by Price Range')
    plt.xlabel('Price Range')
    plt.ylabel('Average Availability')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('availability_by_price_range.png', dpi=300, bbox_inches='tight')
    
    # Conclusion
    print("\nConclusion:")
    
    # Determine if cheaper or more expensive books tend to have higher availability
    price_availability_trend = "unclear"
    if corr_price > 0.1:
        price_availability_trend = "More expensive books tend to have higher availability"
    elif corr_price < -0.1:
        price_availability_trend = "Cheaper books tend to have higher availability"
    
    print(f"1. {price_availability_trend} (correlation: {corr_price:.4f}).")
    
    # Determine if higher or lower rated books tend to have higher availability
    rating_availability_trend = "unclear"
    if corr_rating > 0.1:
        rating_availability_trend = "Higher-rated books tend to have higher availability"
    elif corr_rating < -0.1:
        rating_availability_trend = "Lower-rated books tend to have higher availability"
    
    print(f"2. {rating_availability_trend} (correlation: {corr_rating:.4f}).")
    
    # Determine which price range has the highest average availability
    highest_availability_price_range = avg_availability_by_price.loc[avg_availability_by_price['Average Availability'].idxmax()]
    print(f"3. Books in the {highest_availability_price_range['Price Range']} price range have the highest average availability ({highest_availability_price_range['Average Availability']:.2f} books).")
    
    # Determine which rating has the highest average availability
    highest_availability_rating = avg_availability_by_rating.loc[avg_availability_by_rating['Average Availability'].idxmax()]
    print(f"4. Books with a rating of {highest_availability_rating['Rating']} have the highest average availability ({highest_availability_rating['Average Availability']:.2f} books).")
    
    # General conclusion
    print("\nOverall Interpretation:")
    print("This analysis provides insights into the inventory management strategy of the bookstore. " +
          "The findings suggest whether the store stocks more of certain types of books based on price or rating, " +
          "which could indicate anticipated demand patterns or strategic inventory decisions.")
    
    conn.close()
    print("\nAvailability analysis complete. Visualizations saved as PNG files.")

if __name__ == "__main__":
    run_availability_analysis()