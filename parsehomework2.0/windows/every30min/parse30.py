from selenium import webdriver
from bs4 import BeautifulSoup
import json
import os
import time
import re

COOKIES_FILE = "cookies.json"

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filename}.")

def load_cookies_from_file(driver, filename):
    """Load cookies into a Selenium browser instance."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print("No cookies file found.")

def login_via_browser(url, cookies_file):
    """Open a browser for manual login and save cookies."""
    driver = webdriver.Chrome()  # Adjust for your browser driver if not using Chrome
    driver.get(url)

    print("Please log in manually. The browser will close automatically after login.")
    input("Press Enter after logging in to save cookies...")
    cookies = driver.get_cookies()
    save_cookies_to_file(cookies, cookies_file)
    driver.quit()

def fetch_homework_section(url, cookies_file):
    """Fetch the specific section of the homework page using Selenium."""
    driver = webdriver.Chrome()

    # Load cookies and navigate to the page
    driver.get(url)
    load_cookies_from_file(driver, cookies_file)
    driver.get(url)
    time.sleep(5)  # Allow the page to load completely

    # Get the HTML content of the page
    html_content = driver.page_source
    driver.quit()
    return html_content

def save_homeworks_by_day(html_content):
    """Identify the day in Russian and save corresponding homework into .txt files."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Map Russian days of the week to English file names
    day_mapping = {
        "Понедельник": "Monday.txt",
        "Вторник": "Tuesday.txt",
        "Среда": "Wednesday.txt",
        "Четверг": "Thursday.txt",
        "Пятница": "Friday.txt",
        "Суббота": "Saturday.txt",
        "Воскресенье": "Sunday.txt",
    }

    # Find all <div> with the class "diary-emotion-cache-mqvnnf-homeworksForDayWrapper"
    day_wrappers = soup.find_all("div", class_="diary-emotion-cache-mqvnnf-homeworksForDayWrapper")

    if not day_wrappers:
        print("No homework sections found.")
        return

    for day_wrapper in day_wrappers:
        day_text = day_wrapper.get_text(separator="\n", strip=True)

        for russian_day, file_name in day_mapping.items():
            if russian_day in day_text:
                # Find all homework cards with the specified class
                homework_cards = day_wrapper.find_all("div", class_="diary-emotion-cache-nl8na2-homeworkCard")

                # Extract and process homework items from each homework card
                homework_items = []
                for card in homework_cards:
                    # Extract text and clean up the content
                    card_text = card.get_text(separator=":\n", strip=True)

                    # Filter out timestamps and unnecessary text
                    filtered_items = [
                        item.strip()
                        for item in card_text.split("\n")
                        if item.strip() and not re.search(r'\d{1,2}:\d{2}', item)  # Exclude lines with time (e.g., 14:30)
                    ]

                    # Add the filtered items and a separator (dashes) between homework cards
                    homework_items.extend(filtered_items)
                    homework_items.append("-" * 30)  # Add a separator line of dashes

                # Write the Russian day name first, followed by homework items
                with open(f"{russian_day}.txt", "w", encoding="utf-8") as file:
                    file.write(f"{russian_day}: \n \n")  # Write the Russian day name
                    for item in homework_items:
                        file.write(f"{item}\n")

                print(f"Saved homework for {russian_day} to {russian_day}.txt.")
                break

def debug_html(html_content):
    """Save the HTML content for debugging."""
    with open("debug.html", "w", encoding="utf-8") as file:
        file.write(html_content)

def main():
    login_url = "https://ms-edu.tatar.ru/16/"  # Replace with actual login URL
    homework_url = "https://ms-edu.tatar.ru/diary/homeworks/homeworks/"

    # Check if cookies exist; otherwise, prompt for manual login
    if not os.path.exists(COOKIES_FILE):
        print("No saved cookies found. Opening browser for manual login.")
        login_via_browser(login_url, COOKIES_FILE)

    while True:
        # Fetch the homework page's specific section
        html_content = fetch_homework_section(homework_url, COOKIES_FILE)

        # Save raw HTML for debugging
        debug_html(html_content)

        # Save homework by day
        save_homeworks_by_day(html_content)

        print("Data parsed and saved. Waiting 30 minutes for the next fetch...")
        time.sleep(1800)  # Wait 30 minutes

if __name__ == "__main__":
    main()