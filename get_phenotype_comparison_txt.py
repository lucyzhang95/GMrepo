from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import glob

t_start = time.time()
base_download_dir = os.path.abspath("downloads")
download_dir = os.path.join(base_download_dir, "phenotype_comparisons")
os.makedirs(download_dir, exist_ok=True)

# headless auto-download setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# phenotype comparison website (microbe-disease relationships)
driver.get("https://gmrepo.humangut.info/phenotypes/comparisons")

# expand the page to include all phenotype comparisons (100 items per page)
try:
    show_100 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='100']]"))
    )
    show_100.click()
    print("Clicked '100' to show all comparisons.")
except Exception as e:
    print("Could not find '100' button:", e)
    driver.quit()
    exit()

# get all phenotype comparison links
wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/phenotypes/comparisons/')]")))
comparison_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/phenotypes/comparisons/')]")
total_links = list(set([link.get_attribute("href") for link in comparison_links if "view details" in link.text.lower()]))
print(f"Found {len(total_links)} comparison links.")

# download txt files
for url in total_links:
    driver.get(url)
    print(f"Processing: {url}")
    time.sleep(3)

    # "All" button contains both species and genus related to the phenotype/disease
    try:
        all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'All')]/input")))
        driver.execute_script("arguments[0].click();", all_button)
    except:
        print("'All' button not found or not clickable.")
        continue
    time.sleep(2)

    # download txt files (txt instead of tsv showed on website)
    try:
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@ng-click, 'downloadNgTable')]")))
        download_button.click()
        print("Downloading...")

        time.sleep(5)
    except:
        print("Download button not found.")

driver.quit()

t_end = time.time()
total_time = t_end - t_start
print("Done.")

download_dir = "downloads"
txt_files = glob.glob(f"{download_dir}/*.txt")
if len(txt_files) == len(total_links):
    print(f"All {len(txt_files)} text files are downloaded.")
else:
    print(f"{len(total_links) - len(txt_files)} text files are missing.")

print(f"Total time spent for download: {total_time/60} minutes.")