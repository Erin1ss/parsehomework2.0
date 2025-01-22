from selenium import webdriver
import json
import os

COOKIES_FILE = "C:\cookies.json"

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file, indent=4, ensure_ascii=False)
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

def main():
    url = "https://ms-edu.tatar.ru/login/"  # Замените на ваш URL
    driver = webdriver.Chrome()  # Настройте драйвер под вашу систему
    driver.get(url)
    
    print("Please log in manually. The browser will close automatically after login.")
    input("Press Enter after logging in to save cookies...")
    
    # Сохраняем куки
    cookies = driver.get_cookies()
    save_cookies_to_file(cookies, COOKIES_FILE)
    
    driver.quit()

if __name__ == "__main__":
    main()
