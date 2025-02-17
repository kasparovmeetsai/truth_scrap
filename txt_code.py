from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from IPython.display import display
import time
from datetime import datetime, timedelta


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
    # Open Trump's Truth Social profile page
    url = "https://truthsocial.com/@realDonaldTrump"
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(5)

    # Scroll down slightly to ensure posts are visible
    driver.execute_script("window.scrollBy(0, 500);")  
    time.sleep(2)

    # Locate the latest 10 posts
    posts = driver.find_elements(By.XPATH, "//div[contains(@class, 'status cursor-pointer focusable')]")[:10]
    
    # Get the current UTC time
    current_time = datetime.utcnow()

    for i, post in enumerate(posts):
        try:
            # Locate timestamp inside each post
            timestamp_element = post.find_element(By.XPATH, ".//time")

            # Extract timestamp from 'title' attribute
            timestamp_text = timestamp_element.get_attribute("title")
            if not timestamp_text:
                print(f"Warning: No timestamp found for post {i+1}")
                continue  # Skip this post

            # Convert timestamp to datetime object
            post_time = datetime.strptime(timestamp_text, "%b %d, %Y, %I:%M %p")

            # Convert post_time to UTC (Assuming it's in EST)
            post_time_utc = post_time  # Adjust timezone conversion if needed

            # Calculate time difference
            time_difference = (current_time - post_time_utc).total_seconds()

            # If post is less than 50 seconds old, take a screenshot
            if time_difference < 50:
                post.screenshot(f"trump_post_{i+1}.png")
                print(f"Captured new post (posted {int(time_difference)}s ago) - Saved as trump_post_{i+1}.png")

                # Display the screenshot in Jupyter Notebook
                img = Image.open(f"trump_post_{i+1}.png")
                display(img)

        except Exception as e:
            print(f"Error processing post {i+1}: {e}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()  # Close the browser
