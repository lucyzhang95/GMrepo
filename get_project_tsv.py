from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import get_project_links
import time
import os
import glob

t_start = time.time()
base_download_dir = os.path.abspath("downloads")
download_dir = os.path.join(base_download_dir, "projects")
os.makedirs(download_dir, exist_ok=True)

options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
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
# driver.set_page_load_timeout(240)
driver.get("https://gmrepo.humangut.info/data/curatedprojects")
time.sleep(2)

# click the checkbox for "Except for..."
try:
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "isInvertedSearch"))
    )
    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(1)
except NoSuchElementException:
    print("Checkbox is not clicked.")

# enter "Health" as key to filter out Health control results
try:
    key = "Health"
    searchbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mySearchTerm"))
    )
    searchbox.clear()
    searchbox.send_keys(key)
    print(f"Search term `{key}` entered")
    time.sleep(1)
except NoSuchElementException:
    print("Searchbox is not found.")

# TODO: need to add code block to click search button to exclude "Health" results
try:
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.input-group-btn button.btn.btn-default[type='submit']"))
    )
    search_button.click()
    print(f"Search button clicked!")
except NoSuchElementException:
    raise Exception("Search button is not found/clickable.")

# expand to show 100 results
try:
    expand_100 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='100']]"))
    )
    expand_100.click()
    print("Clicked '100' to show all disease projects.")
    time.sleep(2)
except NoSuchElementException:
    print("Could not find '100' button.")

# get project ids and hrefs per phenotype/disease under that project
all_project_links = {}
p_num = 1

while True:
    print(f"Scraping page {p_num}...")
    p_proj_links = get_project_links(driver, wait)
    all_project_links.update(p_proj_links)

    try:
        nxt = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'page-item')]/a[normalize-space(text())='»']"))
        )
        parent_li = nxt.find_element(By.XPATH, "./ancestor::li")
        if "disabled" in parent_li.get_attribute("class"):
            print("Last page reached.")
            break
        print("Going to next page...")
        nxt.click()
        time.sleep(3)
        p_num += 1
    except Exception as e:
        print(f"No next button found or an error occurred: {e}")
        break

link_ct = sum([len(link) for link in all_project_links.values()]) # 04042025: 100 projects with 127 links on page 1 and 56 links on page 2
print(f"Found {len(all_project_links)} projects with a total of {link_ct} links.")
print(f"First project link: {all_project_links[0]}")
