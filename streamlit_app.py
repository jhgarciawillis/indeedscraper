import streamlit as st
import pandas as pd
from indeed_job_scraper import get_indeed_job_listings
from data_processor import process_indeed_data

def main():
    st.title("Indeed Job Scraper and Analyzer")

    # Sidebar for search parameters
    st.sidebar.header("Search Parameters")
    
    # Job search terms
    search_terms = st.sidebar.text_area("Enter job search terms (one per line):",
                                        "python\ndata science\nmachine learning")
    terms = [term.strip() for term in search_terms.split('\n') if term.strip()]

    # Locations
    locations = st.sidebar.text_area("Enter locations (one per line):",
                                     "México\nNuevo León\nCiudad de México")
    locations = [loc.strip() for loc in locations.split('\n') if loc.strip()]

    # Home office option
    home_office = st.sidebar.checkbox("Search for home office jobs only")

    # Scraping button
    if st.sidebar.button("Start Scraping"):
        if terms and locations:
            with st.spinner("Scraping job listings... This may take a while."):
                job_listings = get_indeed_job_listings(terms, locations, home_office)
                processor = process_indeed_data(job_listings)
                st.session_state['processor'] = processor
                st.success(f"Scraped {len(job_listings)} job listings!")
        else:
            st.error("Please enter at least one search term and one location.")

    # Display results if data is available
    if 'processor' in st.session_state:
        processor = st.session_state['processor']
        
        # Summary statistics
        st.header("Summary Statistics")
        stats = processor.get_summary_stats()
        st.write(stats)

        # Job filtering
        st.header("Filter Jobs")
        col1, col2 = st.columns(2)
        with col1:
            min_salary = st.number_input("Minimum Salary", min_value=0, value=0, step=1000)
            job_type = st.selectbox("Job Type", ['All'] + list(processor.df['Job Type'].unique()))
        with col2:
            max_salary = st.number_input("Maximum Salary", min_value=0, value=1000000, step=1000)
            location = st.text_input("Location")
        work_from_home = st.checkbox("Work From Home")

        filtered_df = processor.filter_jobs(
            min_salary=min_salary if min_salary > 0 else None,
            max_salary=max_salary if max_salary < 1000000 else None,
            job_type=job_type if job_type != 'All' else None,
            location=location if location else None,
            work_from_home=work_from_home if work_from_home else None
        )

        # Display filtered results
        st.subheader(f"Filtered Results ({len(filtered_df)} jobs)")
        st.dataframe(filtered_df)

        # Export to Excel
        if st.button("Export to Excel"):
            processor.save_to_excel("job_listings.xlsx")
            st.success("Data exported to job_listings.xlsx")

if __name__ == "__main__":
    main()