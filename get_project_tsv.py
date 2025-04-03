from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import glob

t_start = time.time()
base_download_dir = os.path.abspath("downloads")
download_dir = os.path.join(base_download_dir, "projects")
os.makedirs(download_dir, exist_ok=True)

options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade":True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# link for curated projects (168) - 81 phenotypes
driver.get("https://gmrepo.humangut.info/data/curatedprojects")

# click the checkbox for "Except for..." selection
try:
    checkbox = driver.find_element(By.ID, "isInvertedSearch")
    checkbox.click()
except NoSuchElementException:
    print("Checkbox is not found.")

#