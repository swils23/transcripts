import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_audio_url(url, username, password):
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    options.add_argument("--auto-open-devtools-for-tabs")
    # mute audio
    options.add_argument("--mute-audio")

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.implicitly_wait(10)

    # fill creds if we end up on the login page
    LOGIN_URL = "signin.k-state.edu"
    if LOGIN_URL in driver.current_url:
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.NAME, "submit").click()

    # eventually we'll end up with a button on the video
    driver.find_element(By.CLASS_NAME, "mediasite-player__playcover-play-button").click()

    # Capture network requests (this part needs DevTools Protocol or additional tools)
    time.sleep(5)  # Wait for requests to complete
    # Retrieve network logs
    logs = driver.get_log("performance")
    driver.close()

    # Filter for manifest requests
    manifest_requests = [entry for entry in logs if "manifest" in entry["message"]]

    for request in manifest_requests:
        print(request)
        with open("manifest.txt", "w") as f:
            f.write(request)

    time.sleep(600)


def get_creds():
    # Check for a .creds file in the data/ directory
    if not os.path.exists("data/.creds"):
        print("Creating a .creds file in the data/ directory")
        with open("data/.creds", "w") as f:
            username = input("Enter your K-State eID: ")
            password = input("Enter your K-State password: ")
            f.write(f"{username}\n{password}")
    else:
        with open("data/.creds", "r") as f:
            username = f.readline().strip()
            password = f.readline().strip()

    return username, password


def main():
    if len(sys.argv) < 2:
        print("Usage: python url.py <url> <url> ...")
        sys.exit(1)
    username, password = get_creds()
    for url in sys.argv[1:]:
        get_audio_url(url, username, password)


if __name__ == "__main__":
    main()
