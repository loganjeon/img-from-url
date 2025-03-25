# Product Image Crawler

This Python script crawls and downloads product images from a given web URL. It uses Selenium and BeautifulSoup to extract images, including those loaded dynamically.

## Features

- Crawls all image tags (`<img>`) from web pages
- Extracts dynamically loaded images
- Option to download only images above a certain size
- Extracts images from inside iframes
- Attempts to download protected images
- Removes ? and subsequent characters from filenames

## Installation

1. You need Python 3.6 or higher installed.
2. Install the required libraries:
3. Chrome browser must be installed (WebDriver will be installed automatically).
4. Clone this repository or download the `product_image_crawler.py` file.

## Usage

1. Open a terminal or command prompt and navigate to the directory containing the script.
2. Run the script with the following command:

- `[URL]`: URL of the webpage to crawl (required)
- `[OUTPUT_FOLDER]`: Folder to save images (optional, default: 'product_images')
- `[MIN_WIDTH]`: Minimum width of images to download (optional, default: 0)
- `[MIN_HEIGHT]`: Minimum height of images to download (optional, default: 0)
3. Example:
4. When the script runs, it will create the specified output folder and save the downloaded images there.

## Command Line Options
- `url`: URL of the webpage to crawl (required)
- `-o, --output`: Folder to save images (optional, default: 'product_images')
- `-W, --min-width`: Minimum width of images to download (optional, default: 0)
- `-H, --min-height`: Minimum height of images to download (optional, default: 0)
- `-h, --help`: Display help message

## Advanced Features
- **Session Maintenance**: Maintains website cookies to access protected images.
- **iframe Processing**: Crawls images inside iframes.
- **Specific Image Download**: Attempts to download images from specific URLs directly.
- **Filename Cleaning**: Removes ? and subsequent characters from downloaded image filenames.

## Cautions
- Use this script in compliance with the website's terms of service.
- Some websites use image protection mechanisms to prevent crawling.
- Excessive requests can burden website servers, so use at appropriate intervals.
- Respect the copyright of downloaded images and use them for personal purposes only.
- For websites that load content dynamically, the script may not capture all images.

## Troubleshooting
- **Images not downloading**: The website may be using image protection mechanisms. Try adding the image URL directly to the `specific_urls` list in the code.
- **Script execution errors**: Ensure all required libraries are installed.
- **Empty images downloaded**: Some websites load images dynamically, try increasing the page loading wait time.

## License
This project is distributed under the MIT License. See the `LICENSE` file for details.

## Contributions
Bug reports, feature requests, pull requests, and all other forms of contribution are welcome. For major changes, please open an issue first to discuss what you would like to change.


# img-from-url
