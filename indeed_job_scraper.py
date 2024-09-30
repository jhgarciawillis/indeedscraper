import urllib.parse
import time
import random
import re
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

    def generate_search_urls(self, terms, locations, home_office=False):
        print("Generating search URLs...")
        search_urls = []
        for term in terms:
            for location in locations:
                url = self._generate_indeed_url(term, location, home_office)
                search_urls.append(url)
        return search_urls

    def _generate_indeed_url(self, term, location, home_office=False):
        print(f"Generating URL for term: {term}, location: {location}, home_office: {home_office}")
        base_url = "https://mx.indeed.com/jobs"
        query = urllib.parse.quote(term)
        location = urllib.parse.quote(location)
        url = f"{base_url}?q={query}&l={location}"
        if home_office:
            url += "&sc=0kf%3Aattr%28DSQF7%29%3B"
        print(f"Generated URL: {url}")
        return url

    def scrape_job_links(self, search_urls):
        print("Starting job link scraping process...")
        all_job_links = []
        for url in search_urls:
            job_links = self._get_job_links(url)
            all_job_links.extend(job_links)
            time.sleep(random.uniform(3, 5))  # Random delay between searches
        print(f"Scraped a total of {len(all_job_links)} job links")
        return all_job_links

    def _get_job_links(self, url):
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

    def scrape_job_details(self, job_links):
        print("Starting job details scraping process...")
        job_listings = []
        for url in job_links:
            job_details = self._scrape_single_job(url)
            if job_details:
                job_listings.append(job_details)
            time.sleep(random.uniform(1, 3))
        print(f"Scraped details for {len(job_listings)} jobs")
        return job_listings

    def _scrape_single_job(self, url):
        print(f"Scraping data from URL: {url}")
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title"))
            )

            job_title = self.driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title").text
            company_name, company_rating, review_count = self._get_company_info()
            work_from_home = self._get_work_from_home(company_name)
            salary_min, salary_max, salary_period = self._get_salary()
            job_type = self._get_job_type()
            location = self._get_location()
            benefits = self._extract_benefits()

            return {
                'Job Title': job_title,
                'Company Name': company_name,
                'Company Rating': company_rating,
                'Review Count': review_count,
                'Salary Min': salary_min,
                'Salary Max': salary_max,
                'Salary Period': salary_period,
                'Job Type': job_type,
                'Location': location,
                'Work From Home': work_from_home,
                'Benefits': benefits,
                'URL': url
            }

        except Exception as e:
            print(f"An error occurred while scraping data from URL: {url} - {e}")
            return None

    def _get_company_info(self):
        try:
            company_name_element = self.driver.find_element(By.CSS_SELECTOR, "div[data-company-name='true'] a")
            company_name = company_name_element.text.strip()
            company_url = company_name_element.get_attribute('href')
            
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "span.css-ppxtlp")
                rating = float(rating_element.text.strip())
                company_rating = f"{rating:.1f}"
                
                original_window = self.driver.current_window_handle
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(company_url)
                
                wait = WebDriverWait(self.driver, 10)
                reviews_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='reviews-countLink']")))
                
                reviews_text = reviews_element.text
                review_count = int(re.search(r'\d+', reviews_text.replace(',', '')).group())
                
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
            except Exception as e:
                print(f"Error getting rating or review count: {e}")
                company_rating = "Not Available"
                review_count = "Not Available"
            
            return company_name, company_rating, review_count
        except Exception as e:
            print(f"Error getting company info: {e}")
            return "Not Found", "Not Available", "Not Available"

    def _get_work_from_home(self, company_name):
        try:
            work_from_home_element = self.driver.find_element(By.CSS_SELECTOR, "div.css-17cdm7w")
            if "Home Office (Desde casa)" in work_from_home_element.text and "Home Office (Desde casa)" not in company_name:
                return "Y"
            else:
                return "N"
        except:
            return "N"

    def _get_salary(self):
        try:
            salary_element = self.driver.find_element(By.CSS_SELECTOR, "span.css-19j1a75")
            salary_text = salary_element.text.strip()
            
            numbers = re.findall(r'\$?([\d,]+(?:\.\d{2})?)', salary_text)
            numbers = [float(n.replace(',', '')) for n in numbers]
            
            if 'hora' in salary_text.lower():
                period = 'hora'
            elif 'mes' in salary_text.lower():
                period = 'mes'
            elif 'año' in salary_text.lower():
                period = 'año'
            else:
                period = 'Not specified'
            
            if len(numbers) == 1:
                return 0, f"{numbers[0]:.2f}", period
            elif len(numbers) == 2:
                return f"{numbers[0]:.2f}", f"{numbers[1]:.2f}", period
            else:
                return 0, 0, period
        except:
            return 0, 0, 'Not Found'

    def _get_job_type(self):
        try:
            job_type_element = self.driver.find_element(By.CSS_SELECTOR, "span.css-k5flys")
            return job_type_element.text
        except:
            return "Not Found"

    def _get_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='inlineHeader-companyLocation']")
            return location_element.text
        except:
            return "Not Found"

    def _extract_benefits(self):
        try:
            benefits_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.css-kyg8or")
            benefits = [benefit.text.strip() for benefit in benefits_elements]
            benefits_text = ', '.join(benefits)
            return benefits_text
        except Exception as e:
            print(f"An error occurred in _extract_benefits: {e}")
            return 'Not Found'

    def close(self):
        print("Closing the WebDriver...")
        self.driver.quit()
        print("WebDriver closed.")

def remove_duplicate_links(links):
    print("Removing duplicate links...")
    unique_links = list(dict.fromkeys(links))
    print(f"Removed {len(links) - len(unique_links)} duplicates.")
    return unique_links

def scrape_indeed_jobs(terms, locations, home_office=False):
    scraper = IndeedJobScraper(headless=False)
    
    search_urls = scraper.generate_search_urls(terms, locations, home_office)
    job_links = scraper.scrape_job_links(search_urls)
    unique_job_links = remove_duplicate_links(job_links)
    job_listings = scraper.scrape_job_details(unique_job_links)
    
    scraper.close()
    
    return job_listings

# This function can be called from streamlit_app.py
def get_indeed_job_listings(terms, locations, home_office=False):
    return scrape_indeed_jobs(terms, locations, home_office)