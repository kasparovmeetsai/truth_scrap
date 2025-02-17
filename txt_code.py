from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
from IPython.display import display


# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x3000")  # Increased height to capture more
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)


# Initialize Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Open the Truth Social profile page
    url = "https://truthsocial.com/@realDonaldTrump"
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(5)

    # Locate the specific post element by class name
    post_element = driver.find_element("xpath", "//div[contains(@class, 'status cursor-pointer focusable')]")

    # Scroll the element into view
    driver.execute_script("arguments[0].scrollIntoView(true);", post_element)
    time.sleep(2)  # Give time for it to adjust

    # Take a screenshot of the post
    screenshot_path = "trump_post.png"
    post_element.screenshot(screenshot_path)
    print(f"Screenshot of the post saved as {screenshot_path}")

    # Display the screenshot in Jupyter Notebook
    img = Image.open(screenshot_path)
    display(img)

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()  # Close the browser
