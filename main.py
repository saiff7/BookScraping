import os
import subprocess
import time

def run_full_analysis():
    """Run the complete book analysis pipeline"""
    print("="*50)
    print("BOOKS TO SCRAPE - COMPREHENSIVE DATA ANALYSIS")
    print("="*50)
    print("\nStarting analysis pipeline...\n")
    
    # Check if database exists
    db_exists = os.path.exists('books.db')
    
    if not db_exists:
        print("Step 1: Web Crawling - Collecting book data...")
        subprocess.run(['python', 'crawler_books_selenium.py'])
    else:
        print("Database already exists. Skipping web crawling step.")
    
    print("\nStep 2: Running Descriptive Analysis...")
    subprocess.run(['python', 'descriptive_analysis.py'])
    
    print("\nStep 3: Running Regression Analysis...")
    subprocess.run(['python', 'regression_analysis.py'])
    
    print("\nStep 4: Running Clustering Analysis...")
    subprocess.run(['python', 'clustering_analysis.py'])
    
    print("\nStep 5: Running Availability Analysis...")
    subprocess.run(['python', 'availability_analysis.py'])
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE!")
    print("="*50)
    print("\nThe following files have been generated:")
    
    # List visualization files
    viz_files = [f for f in os.listdir('.') if f.endswith('.png')]
    for file in viz_files:
        print(f"- {file}")
    
    print("\nYou can now use these results to create your presentation slides.")

if __name__ == "__main__":
    run_full_analysis()