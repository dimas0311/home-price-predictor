from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from datetime import datetime
import os
import re
import random
from fake_useragent import UserAgent
import undetected_chromedriver as uc


class JamesEditionScraper:
    def __init__(self):
        # Use undetected-chromedriver instead of regular ChromeDriver
        options = uc.ChromeOptions()

        # Random User Agent
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')

        # Additional anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-gpu')

        # Add random viewport size
        viewports = [
            (1366, 768),
            (1920, 1080),
            (1536, 864),
            (1440, 900),
            (1280, 720)
        ]
        viewport = random.choice(viewports)
        options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')

        # Initialize undetected-chromedriver
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)  # Increased wait time
        self.eur_to_usd_rate = 1.08
        self.json_filename = f'jamesedition_listings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        # Initialize JSON file with empty array
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump([], f)

        self.total_listings_processed = 0

        # Add cookies and localStorage from a successful session
        self.initial_setup()

    def initial_setup(self):
        """Perform initial setup with cookies and localStorage"""
        try:
            # Visit homepage first
            self.driver.get("https://www.jamesedition.com")
            time.sleep(5)  # Wait for page load

            # Add cookies that might help bypass protection
            cookies = [
                {
                    'name': 'cf_clearance',
                    'value': 'your_cf_clearance_value_here',  # Need to be updated with real value
                    'domain': '.jamesedition.com'
                },
                # Add other cookies as needed
            ]

            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {str(e)}")

        except Exception as e:
            print(f"Error in initial setup: {str(e)}")

    def extract_number_from_text(self, text):
        if not text:
            return 'N/A'
        # Improved number extraction to handle various formats
        numbers = re.findall(r'[\d,]+(?:\.?\d*)?', text)
        if numbers:
            # Remove commas and convert to float
            clean_number = numbers[0].replace(',', '')
            try:
                return float(clean_number)
            except ValueError:
                return 'N/A'
        return 'N/A'

    def convert_sqm_to_sqft(self, sqm_str):
        try:
            # Handle different area formats
            sqm = self.extract_number_from_text(sqm_str)
            if sqm != 'N/A':
                sqft = round(float(sqm) * 10.764, 2)
                return f"{sqft:,.2f} sq ft"
            return "N/A"
        except (ValueError, TypeError):
            return "N/A"

    def convert_eur_to_usd(self, eur_str):
        try:
            eur_amount = float(re.sub(r'[^\d.]', '', eur_str))
            usd_amount = eur_amount * self.eur_to_usd_rate
            return f"${usd_amount:,.2f}"
        except (ValueError, TypeError):
            return "N/A"

    def format_number(self, text, unit=''):
        try:
            number = self.extract_number_from_text(text)
            return f"{float(number):g}{unit}" if number != 'N/A' else 'N/A'
        except (ValueError, TypeError):
            return "N/A"

    def save_listing_to_json(self, listing_data):
        try:
            # Read existing data
            with open(self.json_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Append new listing
            data.append(listing_data)

            # Write back to file
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.total_listings_processed += 1
            print(
                f"Saved listing: {listing_data['address']} (Total processed: {self.total_listings_processed})")
        except Exception as e:
            print(f"Error saving listing to JSON: {str(e)}")

    def extract_listing_data(self, listing):
        try:
            time.sleep(random.uniform(0.5, 1.5))

            # Scroll element into view and wait for it to load
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", listing)
            time.sleep(random.uniform(1, 2))

            # Extract price (unchanged)
            price_eur = listing.find_element(
                By.CLASS_NAME, 'ListingCard__price').text.strip()
            price_usd = self.convert_eur_to_usd(price_eur)
            price_value = ''.join(filter(str.isdigit, price_eur))

            # Improved image extraction
            try:
                # Try multiple selectors for images
                image_selectors = [
                    '.je2-single-slider__slides img.je2-lazy-load',
                    '.je2-single-slider__slides img[src]',
                    '.ListingCard__image img[src]',
                    '.ListingCard__image source[srcset]'
                ]

                image_links = []
                for selector in image_selectors:
                    images = listing.find_elements(By.CSS_SELECTOR, selector)
                    for img in images:
                        # Try both src and data-src attributes
                        src = img.get_attribute(
                            'src') or img.get_attribute('data-src')
                        if src and src.strip() and not src.endswith('placeholder.jpg'):
                            image_links.append(src)
                            break
                    if image_links:
                        break

                image_link = image_links[0] if image_links else 'N/A'
            except Exception as e:
                print(f"Error extracting image: {str(e)}")
                image_link = 'N/A'

            # Improved area extraction
            tags = listing.find_elements(By.CLASS_NAME, 'ListingCard__tag')
            beds = baths = area_sqm = 'N/A'

            # Process all possible area formats
            area_patterns = [
                r'(\d[\d,\.]*)\s*(?:m²|sqm|sq\.m|square meters)',
                r'(\d[\d,\.]*)\s*(?:ft²|sqft|sq\.ft|square feet)'
            ]

            for tag in tags:
                tag_text = tag.text.strip().lower()

                if 'bed' in tag_text:
                    beds = self.format_number(tag_text, ' beds')
                elif 'bath' in tag_text:
                    baths = self.format_number(tag_text, ' baths')
                else:
                    # Check for area in different formats
                    for pattern in area_patterns:
                        match = re.search(pattern, tag_text, re.IGNORECASE)
                        if match:
                            area_value = match.group(1).replace(',', '')
                            if 'ft' in tag_text:
                                # Convert sq ft to sq m first
                                area_sqm = f"{float(area_value) / 10.764:.2f} sqm"
                            else:
                                area_sqm = f"{float(area_value)} sqm"
                            break

            # Convert area to sq ft
            area_sqft = self.convert_sqm_to_sqft(area_sqm)

            # Extract address (unchanged)
            title_element = listing.find_element(
                By.CLASS_NAME, 'ListingCard__title')
            full_address = title_element.text.strip()
            address_parts = full_address.split(', ')

            address_locality = address_parts[0] if len(
                address_parts) > 0 else ''
            address_region = address_parts[1] if len(address_parts) > 1 else ''
            address_country = address_parts[-1] if len(
                address_parts) > 2 else ''

            # Get listing URL
            home_url = listing.find_element(
                By.CSS_SELECTOR, 'a.js-link').get_attribute('href')

            listing_data = {
                'home_url': home_url,
                'image_link': image_link,
                'address': full_address,
                'price_eur': price_eur,
                'price_usd': price_usd,
                'beds': beds,
                'baths': baths,
                'area_sqm': area_sqm,
                'area_sqft': area_sqft,
                'price_value': price_value,
                'address_locality': address_locality,
                'address_region': address_region,
                'address_country': address_country,
                'timestamp': datetime.now().isoformat()
            }

            self.save_listing_to_json(listing_data)
            return listing_data

        except Exception as e:
            print(f"Error extracting listing data: {str(e)}")
            return None

    def random_sleep(self, min_time=3, max_time=7):
        """Sleep for a random amount of time"""
        time.sleep(random.uniform(min_time, max_time))

    def random_scroll(self):
        """Perform random scrolling behavior"""
        try:
            total_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            viewport_height = self.driver.execute_script(
                "return window.innerHeight")

            current_position = 0
            while current_position < total_height:
                scroll_amount = random.randint(100, 400)
                current_position += scroll_amount
                self.driver.execute_script(
                    f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(0.1, 0.3))

            # Scroll back up randomly
            for _ in range(random.randint(1, 3)):
                random_position = random.randint(0, total_height)
                self.driver.execute_script(
                    f"window.scrollTo(0, {random_position});")
                time.sleep(random.uniform(0.1, 0.3))

        except Exception as e:
            print(f"Error during random scroll: {str(e)}")

    def add_random_mouse_movement(self):
        """Simulate random mouse movements using JavaScript"""
        try:
            script = """
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': arguments[0],
                    'clientY': arguments[1]
                });
                document.dispatchEvent(event);
            """

            # Simulate random mouse movements
            for _ in range(random.randint(5, 10)):
                x = random.randint(0, self.driver.execute_script(
                    "return window.innerWidth;"))
                y = random.randint(0, self.driver.execute_script(
                    "return window.innerHeight;"))
                self.driver.execute_script(script, x, y)
                time.sleep(random.uniform(0.1, 0.3))

        except Exception as e:
            print(f"Error during mouse movement simulation: {str(e)}")

    def scrape_page(self, url, page_number):
        try:
            page_url = url.format(pageNumber=page_number)
            print(f"\nScraping page {page_number}: {page_url}")

            # Add random delay before loading new page
            self.random_sleep(4, 8)

            self.driver.get(page_url)

            # Add random mouse movements and scrolling
            self.add_random_mouse_movement()
            self.random_scroll()

            # Variable wait time
            wait_time = random.uniform(5, 10)
            time.sleep(wait_time)

            # Check for Cloudflare challenge
            if "challenge" in self.driver.current_url or "checking your browser" in self.driver.page_source.lower():
                print("Detected Cloudflare challenge, waiting for resolution...")
                time.sleep(20)  # Wait longer for challenge to resolve

            # Wait for listings with increased timeout
            listings = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'ListingCard')
                )
            )

            print(f"Found {len(listings)} listings on page {page_number}")

            # Process listings with random delays
            processed_listings = []
            for index, listing in enumerate(listings, 1):
                print(
                    f"\nProcessing listing {index} of {len(listings)} on page {page_number}")

                # Random scroll behavior
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", listing)
                self.random_sleep(1, 3)

                listing_data = self.extract_listing_data(listing)
                if listing_data:
                    processed_listings.append(listing_data)

                # Random delay between listings
                self.random_sleep(1, 2)

            return processed_listings

        except TimeoutException:
            print(
                f"Timeout waiting for listings to load on page {page_number}")
            return []
        except Exception as e:
            print(f"Error scraping page {page_number}: {str(e)}")
            return []

    def scrape_all_pages(self, base_url, start_page=0, end_page=50):
        all_listings = []

        for page in range(start_page, end_page + 1):
            try:
                print(f"\n{'='*50}")
                print(f"Starting page {page} of {end_page}")
                print(f"{'='*50}")

                page_listings = self.scrape_page(base_url, page)
                all_listings.extend(page_listings)

                print(
                    f"\nCompleted page {page}. Total listings so far: {self.total_listings_processed}")

                # Random delay between pages
                if page < end_page:
                    # Increased delay between pages
                    delay = random.uniform(10, 15)
                    print(f"Waiting {delay:.1f} seconds before next page...")
                    time.sleep(delay)

            except Exception as e:
                print(f"Error processing page {page}: {str(e)}")
                # On error, wait longer before trying next page
                time.sleep(random.uniform(20, 30))
                continue

        return all_listings

    def close(self):
        self.driver.quit()


def main():
    base_urls = ["https://www.jamesedition.com/real_estate/mexico?real_estate_type[]=house&eur_price_cents_from=49000000&eur_price_cents_to=83706300&page={pageNumber}",
    "",
    "",
    "",
    "",
    "",
    "",]
    "",
    "",

    scraper = JamesEditionScraper()
    try:
        print(
            f"Starting scraping... Output will be saved to: {scraper.json_filename}")

        # Scrape pages with more conservative range
        listings_data = scraper.scrape_all_pages(base_url, 1, 50)

        print(f"\nScraping completed.")
        print(f"Total listings processed: {scraper.total_listings_processed}")
        print(f"Data saved to {scraper.json_filename}")

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
