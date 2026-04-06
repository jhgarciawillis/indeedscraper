import os
import sys
import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import load_workbook
import random

load_dotenv()

random.seed(int(time.time()))


class IndeedJobScraper:
    def __init__(self, mode='append'):
        self.output_file = os.path.join(os.getcwd(), 'job_listings.xlsx')
        self.mode = mode
        self.links_scraped = 0
        self.total_rows = 0 if not os.path.exists(self.output_file) else self._get_existing_row_count()

    def _get_existing_row_count(self):
        if os.path.exists(self.output_file):
            df = pd.read_excel(self.output_file)
            return len(df)
        return 0

    def scrape_job_listings(self, urls, start_line=1):
        print("Starting scrape_job_listings...")
        for index, url in enumerate(urls[start_line - 1:], start=start_line):
            print(f"Scraping data from URL: {url}")
            job_listing = self._scrape_job_details(url)

            if job_listing:
                self._save_to_excel(job_listing)
                self.links_scraped += 1
                self.total_rows += 1
                print(f"Saved job listing {index} to Excel.")
                print(f"Total links scraped in this session: {self.links_scraped}")
                print(f"Total rows in Excel file: {self.total_rows}")

        print("Finished scrape_job_listings.")

    def _scrape_job_details(self, url):
        print("Starting _scrape_job_details...")
        print(f"Scraping data from URL: {url}")

        driver = self._setup_webdriver()

        try:
            print("Navigating to the URL...")
            driver.get(url)

            print("Waiting for the page to load...")
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title")))

            print("Extracting job details...")
            job_title = driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title").text
            company_name, company_rating, review_count = self._get_company_info(driver)
            work_from_home = self._get_work_from_home(driver, company_name)
            salary_min, salary_max, salary_period = self._get_salary(driver)
            job_type = self._get_job_type(driver)
            location = self._get_location(driver)
            benefits = self._extract_benefits(driver)

            print("Performing random clicks...")
            self._perform_random_clicks(driver)

            print("Creating job listing dictionary...")
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

        finally:
            print("Closing the WebDriver...")
            driver.quit()

    def _setup_webdriver(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def _perform_random_clicks(self, driver):
        nav_elements = driver.find_elements(By.CSS_SELECTOR, ".gnav-header-1yj7ljr, .css-p2fq43")
        if nav_elements:
            num_clicks = random.randint(1, 3)
            for _ in range(num_clicks):
                random_element = random.choice(nav_elements)
                try:
                    random_element.click()
                    time.sleep(random.uniform(1, 3))
                    driver.back()
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Failed to click on random element: {e}")

    def _get_company_info(self, driver):
        try:
            company_name_element = driver.find_element(By.CSS_SELECTOR, "div[data-company-name='true'] a")
            company_name = company_name_element.text.strip()
            company_url = company_name_element.get_attribute('href')
            print(f"Company name: {company_name}")

            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "span.css-ppxtlp")
                rating = float(rating_element.text.strip())
                company_rating = f"{rating:.1f}"
                print(f"Company rating: {company_rating}")

                original_window = driver.current_window_handle
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(company_url)

                wait = WebDriverWait(driver, 10)
                reviews_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='reviews-countLink']")))

                reviews_text = reviews_element.text
                review_count = int(re.search(r'\d+', reviews_text.replace(',', '')).group())
                print(f"Number of evaluations: {review_count}")

                driver.close()
                driver.switch_to.window(original_window)

            except Exception as e:
                print(f"Error getting rating or review count: {e}")
                company_rating = "Not Available"
                review_count = "Not Available"

            return company_name, company_rating, review_count
        except Exception as e:
            print(f"Error getting company info: {e}")
            return "Not Found", "Not Available", "Not Available"

    def _get_work_from_home(self, driver, company_name):
        try:
            work_from_home_element = driver.find_element(By.CSS_SELECTOR, "div.css-17cdm7w")
            if "Home Office (Desde casa)" in work_from_home_element.text and "Home Office (Desde casa)" not in company_name:
                return "Y"
            else:
                return "N"
        except:
            return "N"

    def _get_salary(self, driver):
        try:
            salary_element = driver.find_element(By.CSS_SELECTOR, "span.css-19j1a75")
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

    def _get_job_type(self, driver):
        try:
            job_type_element = driver.find_element(By.CSS_SELECTOR, "span.css-k5flys")
            return job_type_element.text
        except:
            return "Not Found"

    def _get_location(self, driver):
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, "div[data-testid='inlineHeader-companyLocation']")
            return location_element.text
        except:
            return "Not Found"

    def _extract_benefits(self, driver):
        print("Starting _extract_benefits...")
        try:
            print("Finding the benefits elements...")
            benefits_elements = driver.find_elements(By.CSS_SELECTOR, "li.css-kyg8or")
            print("Extracting the benefits text...")
            benefits = [benefit.text.strip() for benefit in benefits_elements]
            print("Joining the benefits into a single string...")
            benefits_text = ', '.join(benefits)
            print("Returning the benefits text...")
            return benefits_text
        except Exception as e:
            print(f"An error occurred in _extract_benefits: {e}")
            return 'Not Found'

    def _save_to_excel(self, job_listing):
        df = pd.DataFrame([job_listing])
        
        if not os.path.exists(self.output_file) or (self.mode == 'rewrite' and not os.path.exists(self.output_file)):
            # If the file doesn't exist or if we're rewriting, create the file from scratch
            df.to_excel(self.output_file, index=False)
            print(f"Created new Excel file and saved job listing.")
        else:
            # If the file exists and we're appending, determine the correct starting row
            with pd.ExcelWriter(self.output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                # Load existing Excel file
                existing_df = pd.read_excel(self.output_file)
                # Start appending after the last row of existing data
                start_row = len(existing_df) + 1
                df.to_excel(writer, index=False, header=False, startrow=start_row)
                print(f"Appended job listing to the existing Excel file.")

class InputHandler:
    @staticmethod
    def get_start_file():
        while True:
            file_choice = input("Which input file do you want to start from? (1-8): ")
            if file_choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return int(file_choice)
            else:
                print("Invalid input. Please enter a number between 1 and 8.")

    @staticmethod
    def get_file_mode():
        while True:
            mode = input("Do you want to append or rewrite the Excel file? (1 for append, 2 for rewrite): ")
            if mode == '1':
                return 'append'
            elif mode == '2':
                return 'rewrite'
            else:
                print("Invalid input. Please enter 1 for append or 2 for rewrite.")

    @staticmethod
    def get_start_line(file_num):
        while True:
            try:
                start_line = int(input(f"Enter the line number in ind_job_link_{file_num}.txt to start from (1 for beginning): "))
                if start_line < 1:
                    raise ValueError
                return start_line
            except ValueError:
                print("Invalid input. Please enter a positive integer.")

def main():
    print("Starting main...")

    # Get the start file number, file mode, and start line
    start_file = InputHandler.get_start_file()
    file_mode = InputHandler.get_file_mode()

    print("Creating an instance of IndeedJobScraper...")
    scraper = IndeedJobScraper(mode=file_mode)

    for file_num in range(start_file, 9):
        input_file = f'ind_job_link_{file_num}.txt'
        print(f"Processing {input_file}...")

        # Determine the start line for the first file, and 1 for subsequent files
        start_line = InputHandler.get_start_line(file_num) if file_num == start_file else 1

        print(f"Reading URLs from {input_file}...")
        with open(input_file, 'r') as file:
            urls = [line.strip() for line in file.readlines()]

        # Slice the URLs list to start from the specified line
        urls = urls[start_line - 1:]

        print(f"Scraping job listings from {input_file}...")
        scraper.scrape_job_listings(urls, start_line=start_line)

        print(f"Finished processing {input_file}")
        print(f"Total links scraped so far: {scraper.links_scraped}")

    print(f"All job listings saved to {scraper.output_file}")
    print(f"Total links scraped across all files: {scraper.links_scraped}")
    print(f"Total rows in Excel file: {scraper.total_rows}")
    print("Finished main.")

if __name__ == "__main__":
    print("Starting the script...")
    main()
    print("Script finished.")