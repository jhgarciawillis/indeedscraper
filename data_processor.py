import pandas as pd
from typing import List, Dict

class JobDataProcessor:
    def __init__(self):
        self.df = None

    def process_job_listings(self, job_listings: List[Dict]):
        """
        Process the job listings data into a pandas DataFrame.
        """
        print("Processing job listings...")
        self.df = pd.DataFrame(job_listings)
        self._clean_data()
        print(f"Processed {len(self.df)} job listings.")

    def _clean_data(self):
        """
        Clean and standardize the data in the DataFrame.
        """
        print("Cleaning data...")
        # Convert salary to numeric
        self.df['Salary Min'] = pd.to_numeric(self.df['Salary Min'], errors='coerce')
        self.df['Salary Max'] = pd.to_numeric(self.df['Salary Max'], errors='coerce')
        
        # Convert company rating to numeric
        self.df['Company Rating'] = pd.to_numeric(self.df['Company Rating'], errors='coerce')
        
        # Convert review count to numeric
        self.df['Review Count'] = pd.to_numeric(self.df['Review Count'], errors='coerce')
        
        # Standardize Work From Home column
        self.df['Work From Home'] = self.df['Work From Home'].map({'Y': 'Yes', 'N': 'No'})
        
        # Remove any duplicate rows based on URL
        self.df.drop_duplicates(subset=['URL'], keep='first', inplace=True)
        
        print("Data cleaning completed.")

    def get_summary_stats(self):
        """
        Generate summary statistics for the job listings.
        """
        if self.df is None:
            return "No data available. Please process job listings first."
        
        stats = {
            'Total Jobs': len(self.df),
            'Unique Companies': self.df['Company Name'].nunique(),
            'Average Salary (Min)': self.df['Salary Min'].mean(),
            'Average Salary (Max)': self.df['Salary Max'].mean(),
            'Work From Home Jobs': self.df['Work From Home'].value_counts().get('Yes', 0),
            'Top 5 Job Types': self.df['Job Type'].value_counts().head().to_dict(),
            'Top 5 Locations': self.df['Location'].value_counts().head().to_dict(),
        }
        
        return stats

    def filter_jobs(self, min_salary=None, max_salary=None, job_type=None, location=None, work_from_home=None):
        """
        Filter job listings based on given criteria.
        """
        if self.df is None:
            return "No data available. Please process job listings first."
        
        filtered_df = self.df.copy()
        
        if min_salary:
            filtered_df = filtered_df[filtered_df['Salary Max'] >= min_salary]
        
        if max_salary:
            filtered_df = filtered_df[filtered_df['Salary Min'] <= max_salary]
        
        if job_type:
            filtered_df = filtered_df[filtered_df['Job Type'] == job_type]
        
        if location:
            filtered_df = filtered_df[filtered_df['Location'].str.contains(location, case=False, na=False)]
        
        if work_from_home is not None:
            filtered_df = filtered_df[filtered_df['Work From Home'] == ('Yes' if work_from_home else 'No')]
        
        return filtered_df

    def save_to_excel(self, filename: str):
        """
        Save the processed data to an Excel file.
        """
        if self.df is None:
            return "No data available. Please process job listings first."
        
        print(f"Saving data to {filename}...")
        self.df.to_excel(filename, index=False)
        print(f"Data saved to {filename}")

    def load_from_excel(self, filename: str):
        """
        Load data from an Excel file.
        """
        print(f"Loading data from {filename}...")
        self.df = pd.read_excel(filename)
        print(f"Loaded {len(self.df)} job listings from {filename}")

def process_indeed_data(job_listings: List[Dict]):
    """
    Process Indeed job listings data.
    This function can be called from streamlit_app.py
    """
    processor = JobDataProcessor()
    processor.process_job_listings(job_listings)
    return processor