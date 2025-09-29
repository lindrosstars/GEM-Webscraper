from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import logging
import json
import sys

## Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_page(driver):
    """Function to scrape data from a single page."""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'card'))
        )
        logging.info("Bid cards loaded successfully.")
    except Exception as e:
        logging.error(f"Error waiting for bid cards: {e}")
        return []

    bid_cards = driver.find_elements(By.CLASS_NAME, 'card')
    bids_data = []

    for card in bid_cards:
        try:
            bid_number_element = card.find_element(By.CLASS_NAME, 'bid_no_hover')
            bid_number = bid_number_element.text.strip()
            bid_url = bid_number_element.get_attribute('href')

            items_link_elements = card.find_elements(By.XPATH, ".//strong[text()='Items:']/following-sibling::a")

            if items_link_elements:
                items = items_link_elements[0].get_attribute('data-content').strip()
                logging.info(f"Found full 'Items' name for bid: {bid_number}")
            else:
                items_element = card.find_element(By.XPATH, ".//strong[text()='Items:']/parent::div")
                items = items_element.text.replace('Items:', '').strip()
                logging.warning(f"Falling back to original format for 'Items' on bid: {bid_number}")

            quantity_element = card.find_element(By.XPATH, ".//strong[text()='Quantity:']/parent::div")
            quantity = quantity_element.text.replace('Quantity:', '').strip()

            department_element = card.find_element(By.XPATH, ".//strong[text()='Department Name And Address:']/parent::div/following-sibling::div")
            department_name_address = department_element.text.strip()

            start_date = card.find_element(By.CSS_SELECTOR, 'span.start_date').text.strip()
            end_date = card.find_element(By.CSS_SELECTOR, 'span.end_date').text.strip()

            bids_data.append({
                'bid_number': bid_number,
                'bid_url': bid_url,
                'items': items,
                'quantity': quantity,
                'department_details': department_name_address,
                'start_date': start_date,
                'end_date': end_date
            })
        except Exception as e:
            logging.error(f"Could not parse a bid card. Skipping. Error: {e}")
            continue

    return bids_data

def write_to_json(data, filename="scraped_bids.json"):
    """
    Parses a list of dictionaries into a JSON file.
    """
    if not data:
        logging.info("No data to write to JSON file.")
        return

    logging.info(f"Writing data to {filename}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("JSON file created successfully.")
    except Exception as e:
        logging.error(f"Failed to write JSON file: {e}")

def print_to_stdout(data):
    """
    Prints a list of dictionaries as a JSON string to stdout.
    """
    if not data:
        logging.info("No data to print to console.")
        return

    # Print the final list of dictionaries as a JSON string to stdout
    print(json.dumps(data, ensure_ascii=False, indent=4))
    logging.info("Data printed to console.")

def main():
    """Main function to run the scraper."""
    logging.info("Starting the web scraping process with Firefox.")

    all_scraped_bids = []
    driver = None

    try:
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        driver = webdriver.Firefox(options=options)
        url = 'https://bidplus.gem.gov.in/bidresultlists/?lang=english'
        logging.info(f"Navigating to {url}")
        driver.get(url)

        all_scraped_bids = scrape_page(driver)

        while True:
            try:
                sleep_time = random.uniform(3, 8)
                logging.info(f"Pausing for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)

                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.page-link.next'))
                )

                next_button_parent = next_page_button.find_element(By.XPATH, '..')
                if 'disabled' in next_button_parent.get_attribute('class'):
                    logging.info("No next page button found. Exiting pagination loop.")
                    break

                logging.info("Clicking the next page button.")
                next_page_button.click()

                all_scraped_bids.extend(scrape_page(driver))

            except Exception as e:
                logging.error(f"An error occurred during pagination: {e}")
                logging.info("Assuming end of pages and exiting loop.")
                break

    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user (Ctrl+C). Saving data...")
    finally:
        if driver:
            logging.info("Closing the browser.")
            driver.quit()

        logging.info(f"Total bids scraped: {len(all_scraped_bids)}")

        # Call both functions to save to a file AND print to console
        write_to_json(all_scraped_bids)
        print_to_stdout(all_scraped_bids)
        logging.info("Script finished.")

if __name__ == "__main__":
    main()