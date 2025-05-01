import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

def run_regression_analysis():
    """Perform regression analysis to explore relationship between book rating and price"""
    # Connect to the database
    conn = sqlite3.connect('books.db')
    
    # Load data into a pandas DataFrame
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    
    print("=== REGRESSION ANALYSIS: RATING vs PRICE ===")
    print(f"Analyzing {len(books_df)} books to determine if rating affects price\n")
    
    # Create a scatter plot with regression line
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Add jitter to ratings for better visualization
    books_df['rating_jitter'] = books_df['rating'] + np.random.normal(0, 0.1, size=len(books_df))
    
    # Create scatter plot
    sns.scatterplot(x='rating_jitter', y='price', data=books_df, alpha=0.6)
    
    # Add regression line
    sns.regplot(x='rating', y='price', data=books_df, scatter=False, color='red', line_kws={"linewidth": 2})
    
    plt.title('Relationship Between Book Rating and Price')
    plt.xlabel('Rating')
    plt.ylabel('Price (£)')
    plt.xticks([1, 2, 3, 4, 5])
    plt.savefig('rating_price_regression.png', dpi=300, bbox_inches='tight')
    
    # Perform simple linear regression using statsmodels
    model = ols('price ~ rating', data=books_df).fit()
    
    # Display summary statistics
    print("Regression Results:")
    print(model.summary().tables[1])
    
    # Calculate average price by rating
    avg_price_by_rating = books_df.groupby('rating')['price'].agg(['mean', 'count']).reset_index()
    avg_price_by_rating.columns = ['Rating', 'Average Price', 'Number of Books']
    avg_price_by_rating['Average Price'] = avg_price_by_rating['Average Price'].round(2)
    
    print("\nAverage Price by Rating:")
    print(avg_price_by_rating.to_string(index=False))
    
    # Interpret the results
    coefficient = model.params['rating']
    p_value = model.pvalues['rating']
    r_squared = model.rsquared
    
    print("\nInterpretation:")
    
    if p_value < 0.05:
        significance = "statistically significant"
    else:
        significance = "not statistically significant"
        
    print(f"The relationship between book rating and price is {significance} (p-value: {p_value:.4f}).")
    
    if coefficient > 0:
        direction = "positive"
    else:
        direction = "negative"
        
    print(f"There is a {direction} relationship between rating and price (coefficient: {coefficient:.4f}).")
    print(f"For each additional star in rating, the book price changes by approximately £{coefficient:.2f}.")
    print(f"The model explains {r_squared:.2%} of the variation in book prices.")
    
    if r_squared < 0.3:
        strength = "weak"
    elif r_squared < 0.7:
        strength = "moderate"
    else:
        strength = "strong"
        
    print(f"This indicates a {strength} relationship between book rating and price.")
    
    print("\nConclusion:")
    if p_value < 0.05 and r_squared > 0.1:
        print("There appears to be a relationship between book rating and price, though other factors likely play a more significant role in determining book prices.")
    else:
        print("There is little evidence that book rating significantly influences book pricing. Other factors such as genre, author popularity, or book length may be more important determinants of price.")
    
    conn.close()
    print("\nRegression analysis complete. Visualization saved as 'rating_price_regression.png'.")

if __name__ == "__main__":
    run_regression_analysis()