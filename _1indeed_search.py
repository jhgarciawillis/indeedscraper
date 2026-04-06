import urllib.parse
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class IndeedJobScraper:
    def __init__(self, headless=False):
        print("Initializing IndeedJobScraper...")
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        print("IndeedJobScraper initialized.")

    def generate_indeed_url(self, term, location, home_office=False):
        print(f"Generating URL for term: {term}, location: {location}, home_office: {home_office}")
        base_url = "https://mx.indeed.com/jobs"
        query = urllib.parse.quote(term)
        location = urllib.parse.quote(location)
        url = f"{base_url}?q={query}&l={location}"
        if home_office:
            url += "&sc=0kf%3Aattr%28DSQF7%29%3B"
        print(f"Generated URL: {url}")
        return url

    def get_job_links(self, url):
        print(f"Getting job links from URL: {url}")
        self.driver.get(url)
        job_links = []
        page_number = 1

        while True:
            print(f"Processing page {page_number}")
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
                )

                job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
                for card in job_cards:
                    try:
                        link = card.find_element(By.CSS_SELECTOR, "a.jcs-JobTitle")
                        href = link.get_attribute('href')
                        if href:
                            job_links.append(href)
                    except NoSuchElementException:
                        print("Failed to find job link in a card")
                        continue

                print(f"Extracted {len(job_links)} job links from page {page_number}")

                try:
                    next_page = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]'))
                    )
                    next_page.click()
                    page_number += 1
                    time.sleep(random.uniform(1, 3))
                except (NoSuchElementException, TimeoutException):
                    print("No more pages to navigate")
                    break
            except TimeoutException:
                print(f"Timeout occurred on page {page_number}. Moving to next URL.")
                break

        return job_links

    def scrape_jobs(self, terms, locations, home_office, job_links_file, append_mode):
        print("Starting job scraping process...")
        all_job_links = []
        for term in terms:
            for location in locations:
                url = self.generate_indeed_url(term, location, home_office)
                job_links = self.get_job_links(url)
                all_job_links.extend(job_links)
                
                # Save links after each term-location combination
                mode = "a" if append_mode else "w"
                with open(job_links_file, mode, encoding="utf-8") as f:
                    for link in job_links:
                        f.write(link + "\n")
                    f.flush()  # Ensure data is written to file
                
                print(f"Saved {len(job_links)} links for '{term}' in '{location}'")
                append_mode = True  # Switch to append mode after first write
                time.sleep(random.uniform(3, 5))  # Random delay between searches
        print(f"Scraped a total of {len(all_job_links)} job links")
        return all_job_links

    def close(self):
        print("Closing the WebDriver...")
        self.driver.quit()
        print("WebDriver closed.")

def main():
    print("Starting main function...")
    terms = ["python", "machine learning", "artificial intelligence",
             "data science", "huggingface", "generative", "RAG", "hft", "kubernetes",
             "docker", "microservices", "spring boot", "high frequency trading", "rpa",
             "gen ai", "ai", "cloud", "google cloud", "aws", "industrial engineer",
             "ingeniero industrial", "lean six sigma"]
    locations = ["México", "Nuevo León", "Baja California", 
                 "Guadalajara", "Querétaro", "Estado de México", 
                 "Guanajuato", "Ciudad de México", "Coahuila"]
    
    home_office = input("Filter for home office jobs only? (y/n): ").lower() == 'y'
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_urls_file = os.path.join(script_dir, "indeed_search_urls.txt")
    job_links_file = os.path.join(script_dir, "indeed_job_links.txt")
    
    # Ask whether to append or start new
    append_mode = input("Append to existing job links file? (y/n): ").lower() == 'y'
    
    scraper = IndeedJobScraper(headless=False)  # Set to True if you want headless mode
    
    print("Generating search URLs...")
    with open(search_urls_file, "w", encoding="utf-8") as f:
        for term in terms:
            for location in locations:
                url = scraper.generate_indeed_url(term, location, home_office)
                f.write(url + "\n")
    
    print(f"Search URLs have been written to {search_urls_file}")
    
    print("Starting job scraping...")
    # Clear the job links file if not in append mode
    if not append_mode:
        open(job_links_file, "w").close()
    
    all_job_links = scraper.scrape_jobs(terms, locations, home_office, job_links_file, append_mode)
    
    scraper.close()
    print(f"All job links have been {'appended to' if append_mode else 'written to'} {job_links_file}")
    print(f"Total number of job links scraped: {len(all_job_links)}")
    print("Main function completed.")

if __name__ == "__main__":
    print("Script started.")
    main()
    print("Script finished.")