from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import re
import random
import pycountry
import json
import os
from datetime import datetime
import time


# Initialize the geocoder with a custom user agent
geolocator = Nominatim(user_agent="real_estate_scraper")

# Cache for geocoding results to avoid repeated API calls
geocoding_cache = {}


def initialize_driver():
    """Initialize Chrome WebDriver with options"""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment if you want headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-webgl')
    options.add_argument('--disable-webgl2')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-accelerated-2d-canvas')
    options.add_argument('--disable-accelerated-video-decode')
    options.add_argument('--disable-gpu-compositing')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-infobars')

    return webdriver.Chrome(options=options)


def get_country_name(country_code):
    """Convert country code to full country name"""
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        return country.name if country else country_code
    except Exception as e:
        print(f"Error getting country name for {country_code}: {str(e)}")
        return country_code


def get_coordinates(city, country_code):
    """Get latitude and longitude for a city and country"""
    cache_key = f"{city},{country_code}".lower()

    # Check cache first
    if cache_key in geocoding_cache:
        return geocoding_cache[cache_key]

    try:
        # Get full country name for better geocoding results
        country_name = get_country_name(country_code)
        location_query = f"{city}, {country_name}"

        # Add delay to respect geocoding service rate limits
        time.sleep(1)

        location = geolocator.geocode(location_query)
        if location:
            result = {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
            # Cache the result
            geocoding_cache[cache_key] = result
            return result
        return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding error for {location_query}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error during geocoding: {str(e)}")
        return None


def load_existing_data(filename):
    """Load existing JSON data if file exists"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"listings": [], "metadata": {"last_updated": None, "total_listings": 0}}
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        return {"listings": [], "metadata": {"last_updated": None, "total_listings": 0}}


def save_to_json(data, filename):
    """Save data to JSON file with proper encoding"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")


def convert_to_usd(price_str):
    """Convert AUD price to USD (using approximate exchange rate)"""
    try:
        amount = float(''.join(filter(str.isdigit, price_str)))
        return round(amount * 0.65, 2)
    except:
        return None


def convert_to_sqft(area_str):
    """Convert square meters to square feet"""
    try:
        sqm = float(re.search(r'([\d.]+)', area_str).group(1))
        return round(sqm * 10.764, 2)
    except:
        return None


def extract_listing_data(listing):
    """Extract data from a single listing element"""
    try:
        # Extract home URL
        home_url = listing.find_element(
            By.CSS_SELECTOR, "div.sc-1dun5hk-0 a").get_attribute("href")

        # Extract image link
        image_link = listing.find_element(
            By.CSS_SELECTOR, "div.img-carousel img").get_attribute("src")

        # Extract price
        price_aud = listing.find_element(
            By.CLASS_NAME, "displayConsumerPrice").text
        price_usd = convert_to_usd(price_aud)

        # Extract features
        features = listing.find_elements(By.CLASS_NAME, "feature-item")
        beds = baths = area = None

        for feature in features:
            feature_text = feature.text
            img_alt = feature.find_element(
                By.TAG_NAME, "img").get_attribute("alt")
            if img_alt == "bedrooms":
                beds = int(feature_text)
            elif img_alt == "bathroom":
                baths = int(feature_text)
            elif img_alt == "buildingSize":
                area = convert_to_sqft(feature_text)

        # Extract address components
        address_elem = listing.find_element(By.CLASS_NAME, "address")
        full_address = address_elem.text
        address_parts = full_address.split(',')

        street_address = address_parts[0].strip()
        city = address_parts[-1].strip()
        country_code = re.search(r'/international/(\w+)/', home_url)
        country_code = country_code.group(1).upper() if country_code else None

        # Get full country name
        country_name = get_country_name(country_code) if country_code else None

        # Get coordinates if we have both city and country
        coordinates = None
        if city and country_code:
            coordinates = get_coordinates(city, country_code)

        # Create listing object with timestamp
        listing_data = {
            'id': hash(f"{home_url}{datetime.now().isoformat()}"),
            'home_url': home_url,
            'image_link': image_link,
            'price_aud': price_aud,
            'price_usd': price_usd,
            'beds': beds,
            'baths': baths,
            'area_sqft': area,
            'address': street_address,
            'city': city,
            'country_code': country_code,
            'country': country_name,
            'latitude': coordinates['latitude'] if coordinates else None,
            'longitude': coordinates['longitude'] if coordinates else None,
            'scraped_at': datetime.now().isoformat()
        }

        return listing_data

    except Exception as e:
        print(f"Error extracting listing data: {str(e)}")
        return None


def scrape_listings(base_urls, max_pages=160, output_file='real_estate_home_data.json'):
    """Main function to scrape listings with real-time JSON updates and country skipping"""
    driver = initialize_driver()

    # Load existing data if any
    data = load_existing_data(output_file)
    existing_urls = {listing['home_url'] for listing in data['listings']}

    # Track skipped countries
    skipped_countries = []

    try:
        for base_url in base_urls:
            country_code = base_url.split(
                '/international/')[1].strip('/').upper()
            country_name = get_country_name(country_code)
            print(f"\nStarting scrape for {country_name} ({country_code})")

            # Flag to track if any listings were found for this country
            country_has_listings = False
            empty_pages_count = 0  # Counter for consecutive empty pages

            for page in range(1, max_pages + 1):
                try:
                    url = f"{base_url}p{page}"
                    driver.get(url)

                    try:
                        # Wait for listings container with shorter timeout
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "sc-1dun5hk-0"))
                        )
                    except Exception:
                        # If no listings container is found, increment empty counter
                        empty_pages_count += 1
                        if empty_pages_count >= 3:  # If 3 consecutive empty pages
                            print(
                                f"No listings found in {country_name} after {page} pages. Skipping...")
                            if not country_has_listings:
                                skipped_countries.append(country_name)
                            break
                        continue

                    # Find all listings on the page
                    listings = driver.find_elements(
                        By.CSS_SELECTOR, "div.sc-1dun5hk-0.cOiOrj")

                    if not listings:
                        empty_pages_count += 1
                        print(
                            f"No listings found on page {page} of {country_name}")
                        if empty_pages_count >= 3:  # If 3 consecutive empty pages
                            print(
                                f"No more listings found in {country_name}. Moving to next country...")
                            if not country_has_listings:
                                skipped_countries.append(country_name)
                            break
                        continue

                    # Reset empty pages counter if we found listings
                    empty_pages_count = 0
                    country_has_listings = True

                    new_listings_count = 0
                    for listing in listings:
                        listing_data = extract_listing_data(listing)

                        if listing_data and listing_data['home_url'] not in existing_urls:
                            data['listings'].append(listing_data)
                            existing_urls.add(listing_data['home_url'])
                            new_listings_count += 1

                            # Update metadata
                            data['metadata'].update({
                                'last_updated': datetime.now().isoformat(),
                                'total_listings': len(data['listings']),
                                'countries_processed': len(set(l['country'] for l in data['listings'])),
                                'countries_skipped': skipped_countries,
                                'average_listings_per_country': len(data['listings']) /
                                max(1, len(set(l['country']
                                    for l in data['listings'])))
                            })

                            # Save after each new listing
                            save_to_json(data, output_file)

                            print(f"Added listing in {listing_data['city']}, {listing_data['country']} "
                                  f"(Lat: {listing_data['latitude']}, Long: {listing_data['longitude']})")

                    if new_listings_count > 0:
                        print(
                            f"Page {page} of {country_name}: Added {new_listings_count} new listings")

                    # Random delay to avoid overwhelming the server
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"Error on page {page} of {country_name}: {str(e)}")
                    empty_pages_count += 1
                    if empty_pages_count >= 3:
                        print(
                            f"Too many errors for {country_name}. Skipping...")
                        if not country_has_listings:
                            skipped_countries.append(country_name)
                        break
                    continue

            # After finishing each country, save a country summary
            country_listings = [l for l in data['listings']
                                if l['country'] == country_name]
            country_summary = {
                'country': country_name,
                'total_listings': len(country_listings),
                'cities': len(set(l['city'] for l in country_listings)),
                'price_range_usd': {
                    'min': min((l['price_usd'] for l in country_listings if l['price_usd']), default=None),
                    'max': max((l['price_usd'] for l in country_listings if l['price_usd']), default=None)
                },
                'completed_at': datetime.now().isoformat()
            }

            # Add country summary to metadata
            if 'country_summaries' not in data['metadata']:
                data['metadata']['country_summaries'] = []
            data['metadata']['country_summaries'].append(country_summary)

            save_to_json(data, output_file)

            print(f"\nCompleted {country_name}:")
            print(f"Total listings: {country_summary['total_listings']}")
            print(f"Cities covered: {country_summary['cities']}")
            if country_summary['price_range_usd']['min']:
                print(f"Price range: ${country_summary['price_range_usd']['min']:,.2f} - "
                      f"${country_summary['price_range_usd']['max']:,.2f} USD")

    except Exception as e:
        print(f"Error during scraping: {str(e)}")

    finally:
        driver.quit()

        # Final save and metadata update
        data['metadata'].update({
            'last_updated': datetime.now().isoformat(),
            'total_listings': len(data['listings']),
            'countries_processed': len(set(l['country'] for l in data['listings'])),
            'countries_skipped': skipped_countries,
            'completion_time': datetime.now().isoformat()
        })
        save_to_json(data, output_file)

        # Print final summary
        print("\nScraping completed!")
        print(f"Total listings: {data['metadata']['total_listings']}")
        print(
            f"Countries processed: {data['metadata']['countries_processed']}")
        print(f"Countries skipped: {len(skipped_countries)}")
        if skipped_countries:
            print("Skipped countries:", ", ".join(skipped_countries))

        return data


if __name__ == "__main__":
    base_urls = [
        "https://www.realestate.com.au/international/bd/",
        "https://www.realestate.com.au/international/pk/",
        "https://www.realestate.com.au/international/mo/",
        "https://www.realestate.com.au/international/lk/",
        "https://www.realestate.com.au/international/vn/",
        "https://www.realestate.com.au/international/kh/",
        "https://www.realestate.com.au/international/id/",
        "https://www.realestate.com.au/international/cn/",
        "https://www.realestate.com.au/international/ph/",
        "https://www.realestate.com.au/international/th/",
        "https://www.realestate.com.au/international/sg/",
        "https://www.realestate.com.au/international/mm/",
        "https://www.realestate.com.au/international/my/",
        "https://www.realestate.com.au/international/il/",
        "https://www.realestate.com.au/international/sa/",
        "https://www.realestate.com.au/international/jo/",
        "https://www.realestate.com.au/international/ae/",
        "https://www.realestate.com.au/international/om/",
        "https://www.realestate.com.au/international/dz/",
        "https://www.realestate.com.au/international/eg/",
        "https://www.realestate.com.au/international/mg/",
        "https://www.realestate.com.au/international/ng/",
        "https://www.realestate.com.au/international/tn/",
        "https://www.realestate.com.au/international/zm/",
        "https://www.realestate.com.au/international/re/",
        "https://www.realestate.com.au/international/mu/",
        "https://www.realestate.com.au/international/gh/",
        "https://www.realestate.com.au/international/bi/",
        "https://www.realestate.com.au/international/cv/",
        "https://www.realestate.com.au/international/ke/",
        "https://www.realestate.com.au/international/za/",
        "https://www.realestate.com.au/international/fj/",
        "https://www.realestate.com.au/international/nz/",
        "https://www.realestate.com.au/international/vu/",
        "https://www.realestate.com.au/international/al/",
        "https://www.realestate.com.au/international/be/",
        "https://www.realestate.com.au/international/cy/",
        "https://www.realestate.com.au/international/fi/",
        "https://www.realestate.com.au/international/gi/",
        "https://www.realestate.com.au/international/ie/",
        "https://www.realestate.com.au/international/lu/",
        "https://www.realestate.com.au/international/nl/",
        "https://www.realestate.com.au/international/pt/",
        "https://www.realestate.com.au/international/sk/",
        "https://www.realestate.com.au/international/ch/",
        "https://www.realestate.com.au/international/gb/",
        "https://www.realestate.com.au/international/tr/",
        "https://www.realestate.com.au/international/si/",
        "https://www.realestate.com.au/international/ro/",
        "https://www.realestate.com.au/international/no/",
        "https://www.realestate.com.au/international/mt/",
        "https://www.realestate.com.au/international/it/",
        "https://www.realestate.com.au/international/gr/",
        "https://www.realestate.com.au/international/fr/",
        "https://www.realestate.com.au/international/bg/",
        "https://www.realestate.com.au/international/ad/",
        "https://www.realestate.com.au/international/at/",
        "https://www.realestate.com.au/international/hr/",
        "https://www.realestate.com.au/international/ee/",
        "https://www.realestate.com.au/international/de/",
        "https://www.realestate.com.au/international/hu/",
        "https://www.realestate.com.au/international/lv/",
        "https://www.realestate.com.au/international/me/",
        "https://www.realestate.com.au/international/pl/",
        "https://www.realestate.com.au/international/rs/",
        "https://www.realestate.com.au/international/es/",
        "https://www.realestate.com.au/international/ag/",
        "https://www.realestate.com.au/international/bs/",
        "https://www.realestate.com.au/international/bo/",
        "https://www.realestate.com.au/international/ky/",
        "https://www.realestate.com.au/international/cr/",
        "https://www.realestate.com.au/international/do/",
        "https://www.realestate.com.au/international/gf/",
        "https://www.realestate.com.au/international/gp/",
        "https://www.realestate.com.au/international/hn/",
        "https://www.realestate.com.au/international/mx/",
        "https://www.realestate.com.au/international/py/",
        "https://www.realestate.com.au/international/kn/",
        "https://www.realestate.com.au/international/vc/",
        "https://www.realestate.com.au/international/tt/",
        "https://www.realestate.com.au/international/uy/",
        "https://www.realestate.com.au/international/ar/",
        "https://www.realestate.com.au/international/bb/",
        "https://www.realestate.com.au/international/br/",
        "https://www.realestate.com.au/international/cl/",
        "https://www.realestate.com.au/international/cw/",
        "https://www.realestate.com.au/international/ec/",
        "https://www.realestate.com.au/international/ge/",
        "https://www.realestate.com.au/international/gt/",
        "https://www.realestate.com.au/international/jm/",
        "https://www.realestate.com.au/international/ni/",
        "https://www.realestate.com.au/international/pe/",
        "https://www.realestate.com.au/international/lc/",
        "https://www.realestate.com.au/international/sx/",
        "https://www.realestate.com.au/international/vg/",
        "https://www.realestate.com.au/international/pr/",
        "https://www.realestate.com.au/international/pa/",
        "https://www.realestate.com.au/international/mq/",
        "https://www.realestate.com.au/international/gd/",
        "https://www.realestate.com.au/international/sv/",
        "https://www.realestate.com.au/international/co/",
        "https://www.realestate.com.au/international/ca/",
        "https://www.realestate.com.au/international/bz/",
        "https://www.realestate.com.au/international/aw/"


        # ... rest of your base URLs
    ]

    results = scrape_listings(base_urls)
    print(
        f"Scraping completed. Total listings: {results['metadata']['total_listings']}")
