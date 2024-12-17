# Hive index community scraper

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# Function to fetch and parse the webpage content
def fetch_page(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

# Function to extract community information
def community_info(driver):
    wait = WebDriverWait(driver, 10)
    community_info = []
    elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/communities/']:not([href='/communities/']):not([href*='/page/'])")

    for element in elements:
        link = element.get_attribute("href")
        match = re.search(r'(\/communities\/[^/]+\/)', link)

        if match:
            result = match.group(1)
            default = driver.find_elements(By.CSS_SELECTOR, f'a[href="{result}"]')[0]
            
            try:
                community_name = default.find_element(By.TAG_NAME, 'h3').text
                container = default.find_element(By.CSS_SELECTOR, 'div').find_element(By.CSS_SELECTOR, 'div').find_elements(By.XPATH, './*')[-1].find_elements(By.XPATH, './*')
                description = default.find_element(By.CSS_SELECTOR, 'div').find_element(By.CSS_SELECTOR, 'div').find_elements(By.XPATH, './*')[1].find_elements(By.CSS_SELECTOR, 'div')[-1].text
                member_count = container[1].text if len(container) > 1 else "0"
                
                tag_elements = container[-1].find_element(By.CSS_SELECTOR, 'div').find_elements(By.XPATH, './*')
                tags = [tag.text for tag in tag_elements]
                
                community_data = {
                    'name': community_name,
                    'description': description,
                    'member_count': member_count,
                    'tags': tags,
                    'url': link
                }
                community_info.append(community_data)
                
            except Exception as e:
                print(f"Error processing community: {e}")
                continue
    
    return community_info

# Function to scrape multiple pages if necessary
def scrape_hive(start_url, pages_to_scrape=1):
    all_communities = []
    driver = None
    
    try:
        for page_num in range(1, pages_to_scrape + 1):
            url = f"{start_url}page/{page_num}" if page_num > 1 else start_url
            print(f"Scraping {url}...")
            
            driver = fetch_page(url)
            communities = community_info(driver)
            all_communities.extend(communities)
            
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        if driver:
            driver.quit()
            
    return all_communities

# Main script to run the scraper
if __name__ == "__main__":
    start_url = "https://thehiveindex.com/communities/"
    communities = scrape_hive(start_url)
    
    # Output the scraped data
    for community in communities:
        print(f"Name: {community['name']}")
        print(f"Description: {community['description']}")
        print(f"Member Count: {community['member_count']}")
        print(f"Tags: {', '.join(community['tags'])}")
        print(f"URL: {community['url']}")
        print("-" * 40)
