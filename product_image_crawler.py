import os
import urllib.parse
import argparse
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.webdriver.chrome.options import Options
import re
from PIL import Image
from io import BytesIO

def clean_filename(filename):
    # Remove ? and subsequent characters
    clean_name = re.sub(r'\?.*$', '', filename)
    # Remove characters that are not allowed in filenames
    clean_name = re.sub(r'[\\/*?:"<>|]', '', clean_name)
    return clean_name

def is_image_large_enough(img_data, min_width, min_height):
    try:
        img = Image.open(BytesIO(img_data))
        width, height = img.size
        return width >= min_width and height >= min_height
    except Exception as e:
        print(f"Error checking image size: {str(e)}")
        return False

def download_product_images(url, output_folder, min_width, min_height):
    # Selenium setup
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-web-security')  # Bypass CORS restrictions
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        
        # Increase page loading wait time
        time.sleep(10)
        
        # Wait until images are loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )
        
        # Scroll to the bottom of the page to load all images
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Get cookies from Selenium session and apply to requests
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        download_count = 0
        skipped_count = 0
        
        # Process regular image tags
        img_tags = driver.find_elements(By.TAG_NAME, 'img')
        
        # Find elements with data-gjs-type="image" attribute
        data_imgs = driver.find_elements(By.CSS_SELECTOR, '[data-gjs-type="image"]')
        img_tags.extend(data_imgs)
        
        for img in img_tags:
            # Scroll to each image element
            driver.execute_script("arguments[0].scrollIntoView();", img)
            time.sleep(0.5)
            
            img_url = img.get_attribute('src')
            if img_url:
                try:
                    # Convert relative URL to absolute URL
                    img_url = urllib.parse.urljoin(url, img_url)
                    raw_filename = img_url.split('/')[-1]
                    clean_name = clean_filename(raw_filename)
                    
                    # Set headers for image request
                    headers = {
                        'Referer': url,
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Origin': urllib.parse.urlparse(url).netloc,
                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache'
                    }
                    
                    # Download the image
                    response = session.get(img_url, headers=headers)
                    if response.status_code == 200:
                        # Check if image meets minimum size requirements
                        if is_image_large_enough(response.content, min_width, min_height):
                            file_name = os.path.join(output_folder, f"{download_count}_{clean_name}")
                            with open(file_name, 'wb') as handler:
                                handler.write(response.content)
                            print(f"Downloaded: {file_name}")
                            download_count += 1
                        else:
                            skipped_count += 1
                            print(f"Skipped: Image too small (minimum size: {min_width}x{min_height})")
                except Exception as e:
                    print(f"Error downloading {img_url}: {str(e)}")
        
        # Process iframes
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                iframe_imgs = driver.find_elements(By.TAG_NAME, 'img')
                for img in iframe_imgs:
                    img_url = img.get_attribute('src')
                    if img_url:
                        # Image processing code (same as regular image processing)
                        try:
                            # Convert relative URL to absolute URL
                            img_url = urllib.parse.urljoin(url, img_url)
                            raw_filename = img_url.split('/')[-1]
                            clean_name = clean_filename(raw_filename)
                            
                            # Set headers for image request
                            headers = {
                                'Referer': url,
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'Origin': urllib.parse.urlparse(url).netloc,
                                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Connection': 'keep-alive',
                                'Cache-Control': 'no-cache'
                            }
                            
                            # Download the image
                            response = session.get(img_url, headers=headers)
                            if response.status_code == 200:
                                # Check if image meets minimum size requirements
                                if is_image_large_enough(response.content, min_width, min_height):
                                    file_name = os.path.join(output_folder, f"{download_count}_{clean_name}")
                                    with open(file_name, 'wb') as handler:
                                        handler.write(response.content)
                                    print(f"Downloaded: {file_name}")
                                    download_count += 1
                                else:
                                    skipped_count += 1
                                    print(f"Skipped: Image too small (minimum size: {min_width}x{min_height})")
                        except Exception as e:
                            print(f"Error downloading {img_url}: {str(e)}")
                
                driver.switch_to.default_content()
            except Exception as e:
                print(f"Error processing iframe: {str(e)}")
                driver.switch_to.default_content()
        
        # # Try to download specific image URLs directly
        # specific_urls = [
        #     "https://cdn.011st.com/11dims/thumbnail/11src/editorImg/20250321/74888344/1742542594186_E.png"
        # ]
        # for specific_url in specific_urls:
        #     try:
        #         response = session.get(specific_url, headers=headers)
        #         if response.status_code == 200:
        #             raw_filename = specific_url.split('/')[-1]
        #             clean_name = clean_filename(raw_filename)
        #             file_name = os.path.join(output_folder, f"specific_{clean_name}")
                    
        #             with open(file_name, 'wb') as handler:
        #                 handler.write(response.content)
        #             print(f"Downloaded specific URL: {file_name}")
        #             download_count += 1
        #     except Exception as e:
        #         print(f"Error downloading specific URL {specific_url}: {str(e)}")
        
        print(f"Total images downloaded: {download_count}")
        print(f"Total images skipped (too small): {skipped_count}")
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    finally:
        driver.quit()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download product images from a website.')
    parser.add_argument('url', help='URL of the website to crawl')
    parser.add_argument('-o', '--output', default='product_images', 
                        help='Output folder for downloaded images (default: product_images)')
    parser.add_argument('-W', '--min-width', type=int, default=0,
                        help='Minimum width for downloaded images (default: 0, no limit)')
    parser.add_argument('-H', '--min-height', type=int, default=0,
                        help='Minimum height for downloaded images (default: 0, no limit)')
    
    args = parser.parse_args()
    
    print(f"Crawling images from: {args.url}")
    print(f"Images will be saved to: {args.output}")
    print(f"Minimum image size: {args.min_width}x{args.min_height}")
    
    success = download_product_images(args.url, args.output, args.min_width, args.min_height)
    
    if success:
        print("Image crawling completed successfully.")
        return 0
    else:
        print("Image crawling failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
