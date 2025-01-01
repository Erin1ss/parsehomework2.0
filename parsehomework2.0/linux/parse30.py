import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import os
import re

COOKIES_FILE = "cookies.json"

async def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filename}.")


async def load_cookies_from_file(context, filename):
    """Load cookies into a Playwright browser context."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            cookies = json.load(file)
            await context.add_cookies(cookies)
    else:
        print("No cookies file found.")


async def login_via_browser(playwright, url, cookies_file):
    """Open a browser for manual login and save cookies."""
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)

    print("Please log in manually. The browser will close automatically after login.")
    input("Press Enter after logging in to save cookies...")

    cookies = await context.cookies()
    await save_cookies_to_file(cookies, cookies_file)
    await browser.close()


async def fetch_homework_section(playwright, url, cookies_file):
    """Fetch the specific section of the homework page using Playwright."""
    browser = await playwright.chromium.launch()
    context = await browser.new_context()

    # Load cookies and navigate to the page
    await load_cookies_from_file(context, cookies_file)
    page = await context.new_page()
    await page.goto(url)
    await asyncio.sleep(5)  # Allow the page to load completely

    # Get the HTML content of the page
    html_content = await page.content()
    await browser.close()
    return html_content


async def save_homeworks_by_day(html_content):
    """Identify the day in Russian and save corresponding homework into .txt files."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Map Russian days of the week to English file names
    day_mapping = {
        "\u041f\u043e\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u0438\u043a": "Monday.txt",
        "\u0412\u0442\u043e\u0440\u043d\u0438\u043a": "Tuesday.txt",
        "\u0421\u0440\u0435\u0434\u0430": "Wednesday.txt",
        "\u0427\u0435\u0442\u0432\u0435\u0440\u0433": "Thursday.txt",
        "\u041f\u044f\u0442\u043d\u0438\u0446\u0430": "Friday.txt",
        "\u0421\u0443\u0431\u0431\u043e\u0442\u0430": "Saturday.txt",
        "\u0412\u043e\u0441\u043a\u0440\u0435\u0441\u0435\u043d\u044c\u0435": "Sunday.txt",
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


async def debug_html(html_content):
    """Save the HTML content for debugging."""
    with open("debug.html", "w", encoding="utf-8") as file:
        file.write(html_content)


async def main():
    login_url = "https://ms-edu.tatar.ru/16/"  # Replace with actual login URL
    homework_url = "https://ms-edu.tatar.ru/diary/homeworks/homeworks/"

    async with async_playwright() as playwright:
        # Check if cookies exist; otherwise, prompt for manual login
        if not os.path.exists(COOKIES_FILE):
            print("No saved cookies found. Opening browser for manual login.")
            await login_via_browser(playwright, login_url, COOKIES_FILE)

        while True:
            # Fetch the homework page's specific section
            html_content = await fetch_homework_section(playwright, homework_url, COOKIES_FILE)

            # Save raw HTML for debugging
            await debug_html(html_content)

            # Save homework by day
            await save_homeworks_by_day(html_content)

            print("Data parsed and saved. Waiting 30 minutes for the next fetch...")
            await asyncio.sleep(1800)  # Wait 30 minutes


if __name__ == "__main__":
    asyncio.run(main())
