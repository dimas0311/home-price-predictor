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
import random
from collections import defaultdict

COUNTRY_COORDINATES = {
    'Spain': {
        'Madrid': (40.4168, -3.7038),
        'Barcelona': (41.3851, 2.1734),
        'Marbella': (36.5097, -4.8867),
        'Mallorca': (39.6953, 3.0176),
        'Ibiza': (38.9067, 1.4206),
        'Valencia': (39.4699, -0.3763)
    },
    'Italy': {
        'Rome': (41.9028, 12.4964),
        'Milan': (45.4642, 9.1900),
        'Venice': (45.4408, 12.3155),
        'Florence': (43.7696, 11.2558),
        'Lake Como': (45.9937, 9.2706),
        'Tuscany': (43.7711, 11.2486)
    },
    'France': {
        'Paris': (48.8566, 2.3522),
        'Nice': (43.7102, 7.2620),
        'Cannes': (43.5528, 7.0174),
        'Saint-Tropez': (43.2727, 6.6386),
        'Provence': (43.9332, 6.0679),
        'French Riviera': (43.7034, 7.2663)
    },
    'Portugal': {
        'Lisbon': (38.7223, -9.1393),
        'Porto': (41.1579, -8.6291),
        'Algarve': (37.0179, -7.9304),
        'Madeira': (32.7607, -16.9595),
        'Cascais': (38.6967, -9.4207),
        'Sintra': (38.8029, -9.3817)
    },
    'Canada': {
        'Toronto': (43.6532, -79.3832),
        'Vancouver': (49.2827, -123.1207),
        'Montreal': (45.5017, -73.5673),
        'Whistler': (50.1163, -122.9574),
        'Victoria': (48.4284, -123.3656),
        'Calgary': (51.0447, -114.0719)
    },
    'United Kingdom': {
        'London': (51.5074, -0.1278),
        'Edinburgh': (55.9533, -3.1883),
        'Bath': (51.3758, -2.3599),
        'Cotswolds': (51.9308, -1.7028),
        'Oxford': (51.7520, -1.2577),
        'Cambridge': (52.2053, 0.1218)
    },
    'Greece': {
        'Athens': (37.9838, 23.7275),
        'Santorini': (36.3932, 25.4615),
        'Mykonos': (37.4415, 25.3667),
        'Crete': (35.2401, 24.8093),
        'Rhodes': (36.4341, 28.2176),
        'Corfu': (39.6243, 19.9217)
    },
    'Switzerland': {
        'Zurich': (47.3769, 8.5417),
        'Geneva': (46.2044, 6.1432),
        'Zermatt': (46.0207, 7.7491),
        'St. Moritz': (46.4908, 9.8355),
        'Lugano': (46.0037, 8.9511),
        'Gstaad': (46.4750, 7.2858)
    },
    'United Arab Emirates': {
        'Dubai': (25.2048, 55.2708),
        'Abu Dhabi': (24.4539, 54.3773),
        'Palm Jumeirah': (25.1124, 55.1390),
        'Jumeirah Beach': (25.2048, 55.2708),
        'Dubai Marina': (25.0777, 55.1339),
        'Yas Island': (24.4979, 54.6047)
    },
    'Mexico': {
        'Cabo San Lucas': (22.8905, -109.9167),
        'Cancun': (21.1619, -86.8515),
        'Tulum': (20.2114, -87.4654),
        'Puerto Vallarta': (20.6534, -105.2253),
        'Mexico City': (19.4326, -99.1332),
        'Playa del Carmen': (20.6296, -87.0739)
    },
    'South Africa': {
        'Cape Town': (-33.9249, 18.4241),
        'Johannesburg': (-26.2041, 28.0473),
        'Durban': (-29.8587, 31.0218),
        'Stellenbosch': (-33.9321, 18.8602),
        'Camps Bay': (-33.9555, 18.3795),
        'Clifton': (-33.9430, 18.3759)
    },
    'Australia': {
        'Sydney': (-33.8688, 151.2093),
        'Melbourne': (-37.8136, 144.9631),
        'Gold Coast': (-28.0167, 153.4000),
        'Perth': (-31.9505, 115.8605),
        'Byron Bay': (-28.6474, 153.6020),
        'Port Douglas': (-16.4834, 145.4649)
    },
    'Germany': {
        'Berlin': (52.5200, 13.4050),
        'Munich': (48.1351, 11.5820),
        'Hamburg': (53.5511, 9.9937),
        'Frankfurt': (50.1109, 8.6821),
        'Baden-Baden': (48.7604, 8.2408),
        'Sylt': (54.9079, 8.3158)
    },
    'Netherlands': {
        'Amsterdam': (52.3676, 4.9041),
        'Rotterdam': (51.9244, 4.4777),
        'The Hague': (52.0705, 4.3007),
        'Utrecht': (52.0907, 5.1214),
        'Haarlem': (52.3873, 4.6462),
        'Wassenaar': (52.1459, 4.4017)
    }
}


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

        self.coordinate_cache = {}
        self.locality_coordinates = defaultdict(list)

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

    def clean_locality(self, locality):
        """Remove prefixes like 'House in' from locality"""
        prefixes_to_remove = [
            'House in ',
            'Villa in ',
            'Apartment in ',
            'Condo in ',
            'Estate in ',
            'Property in ',
            'Country House in ',
            'Penthouse in '
        ]

        cleaned_locality = locality
        for prefix in prefixes_to_remove:
            if cleaned_locality.startswith(prefix):
                cleaned_locality = cleaned_locality[len(prefix):]
                break

        return cleaned_locality

    def get_base_coordinates(self, address_locality, country):
        """Get base coordinates for a locality, using fuzzy matching for the specific country"""
        clean_locality = address_locality.lower().strip()

        # Check if we have coordinates for this country
        if country in COUNTRY_COORDINATES:
            # Try to match with known cities in the country
            for city, coords in COUNTRY_COORDINATES[country].items():
                if city.lower() in clean_locality or clean_locality in city.lower():
                    return coords

            # If no specific city match found, return coordinates of the first city as default
            return next(iter(COUNTRY_COORDINATES[country].values()))

        # If country not found in coordinates, use a default central point
        print(f"Warning: No coordinates found for country: {country}")
        return (0.0, 0.0)  # Default to null island if no match found

    def generate_random_nearby_coordinates(self, base_lat, base_lon, radius_km=105):
        """Generate random coordinates within a radius of base coordinates"""
        # Convert radius from km to degrees (approximate)
        radius_deg = radius_km / 111.32  # 1 degree is approximately 111.32 km

        # Generate random offsets
        lat_offset = random.uniform(-radius_deg, radius_deg)
        lon_offset = random.uniform(-radius_deg, radius_deg)

        # Add offsets to base coordinates
        new_lat = base_lat + lat_offset
        new_lon = base_lon + lon_offset

        return (round(new_lat, 6), round(new_lon, 6))

    def get_coordinates_for_locality(self, address_locality, full_address, country):
        """Get or generate coordinates for a locality while maintaining consistency"""
        # Create a unique key for this exact location
        location_key = f"{address_locality}_{full_address}_{country}"

        # Return cached coordinates if they exist
        if location_key in self.coordinate_cache:
            return self.coordinate_cache[location_key]

        # Get base coordinates for the locality in the specific country
        base_lat, base_lon = self.get_base_coordinates(
            address_locality, country)

        # Generate new coordinates
        new_coords = self.generate_random_nearby_coordinates(
            base_lat, base_lon)

        # Ensure the new coordinates are unique for this locality
        max_attempts = 10
        attempt = 0
        while (new_coords in self.locality_coordinates[address_locality] and
               attempt < max_attempts):
            new_coords = self.generate_random_nearby_coordinates(
                base_lat, base_lon)
            attempt += 1

        # Store the coordinates
        self.locality_coordinates[address_locality].append(new_coords)
        self.coordinate_cache[location_key] = new_coords

        return new_coords

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
            full_address = self.clean_locality(title_element.text.strip())
            address_parts = full_address.split(', ')

            address_locality = self.clean_locality(
                address_parts[0]) if len(address_parts) > 0 else ''
            address_region = address_parts[1] if len(address_parts) > 1 else ''
            address_country = address_parts[-1] if len(
                address_parts) > 2 else ''
            latitude, longitude = self.get_coordinates_for_locality(
                address_locality, full_address, address_country)

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
                'latitude': latitude,
                'longitude': longitude,
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


def get_base_urls():
    """Returns a dictionary of base URLs for different countries"""
    countries = {
        "Spain": "https://www.jamesedition.com/real_estate/spain",
        "Italy": "https://www.jamesedition.com/real_estate/italy",
        "France": "https://www.jamesedition.com/real_estate/france",
        "Portugal": "https://www.jamesedition.com/real_estate/portugal",
        "Canada": "https://www.jamesedition.com/real_estate/canada",
        "United Kingdom": "https://www.jamesedition.com/real_estate/united-kingdom",
        "Greece": "https://www.jamesedition.com/real_estate/greece",
        "Switzerland": "https://www.jamesedition.com/real_estate/switzerland",
        "United Arab Emirates": "https://www.jamesedition.com/real_estate/united-arab-emirates",
        "Mexico": "https://www.jamesedition.com/real_estate/mexico",
        "South Africa": "https://www.jamesedition.com/real_estate/south-africa",
        "Australia": "https://www.jamesedition.com/real_estate/australia",
        "Germany": "https://www.jamesedition.com/real_estate/germany",
        "Netherlands": "https://www.jamesedition.com/real_estate/netherlands"
    }

    # Add common query parameters to each URL
    base_params = "?real_estate_type[]=house&eur_price_cents_from=49000000&eur_price_cents_to=83706300&page={pageNumber}"
    return {country: url + base_params for country, url in countries.items()}


def main():
    base_urls = get_base_urls()
    scraper = JamesEditionScraper()

    try:
        print(
            f"Starting scraping... Output will be saved to: {scraper.json_filename}")

        all_listings = []
        for country, base_url in base_urls.items():
            print(f"\nScraping {country}...")
            try:
                listings_data = scraper.scrape_all_pages(base_url, 1, 50)
                all_listings.extend(listings_data)
                print(
                    f"Completed scraping {country}. Found {len(listings_data)} listings.")
            except Exception as e:
                print(f"Error scraping {country}: {str(e)}")
                continue

        print(f"\nScraping completed for all countries.")
        print(f"Total listings processed: {scraper.total_listings_processed}")
        print(f"Data saved to {scraper.json_filename}")

    except Exception as e:
        print(f"Fatal error during scraping: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
