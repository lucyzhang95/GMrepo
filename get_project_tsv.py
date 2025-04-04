import csv
import glob
import os
import time

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dump_utils import get_project_links

# TODO: code can be further optimized to run faster (current runtime is ~14 min)

t_start = time.time()
base_download_dir = os.path.abspath("downloads")
download_dir = os.path.join(base_download_dir, "projects")
os.makedirs(download_dir, exist_ok=True)

options = Options()
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
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

try:
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "span.input-group-btn button.btn.btn-default[type='submit']",
            )
        )
    )
    search_button.click()
    print("Search button clicked!")
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
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//li[contains(@class, 'page-item')]/a[normalize-space(text())='»']",
                )
            )
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

link_ct = sum([len(link) for link in all_project_links.values()])
print(f"Found {len(all_project_links)} projects with a total of {link_ct} links.")
# 04042025: Found 145 projects with a total of 183 links.

# export all_project_links to csv
proj_path = os.path.join(download_dir, "GMrepo_project_links.csv")
with open(proj_path, "w", newline="", encoding="utf-8") as csv_f:
    writer = csv.writer(csv_f)
    writer.writerow(["Project_ID", "Page_Link"])
    for project_id, links in all_project_links.items():
        for link in links:
            writer.writerow([project_id, link])
print(f"Exported dictionary to {proj_path}")

# download project phenotype files
for _id, p_urls in all_project_links.items():
    for p_url in p_urls:
        print(f"Processing project {_id} from page: {p_url}")
        driver.get(p_url)
        time.sleep(2)

        try:
            dump_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//a[contains(text(), 'Download stats') and contains(@href, '.tsv.gz')]",
                    )
                )
            )
            dump_url = dump_elem.get_attribute("href")

            resp = requests.get(dump_url, timeout=120)
            resp.raise_for_status()

            dump_fname = os.path.basename(dump_url)
            new_fname = f"{_id}_{dump_fname}"
            new_fpath = os.path.join(download_dir, new_fname)

            with open(new_fpath, "wb") as f:
                f.write(resp.content)
            print(f"Downloaded {dump_fname} to {new_fpath}")
        except Exception as e:
            print(f"Failed to download {dump_fname} from page {p_url}: {e}")

t_end = time.time()
total_time = t_end - t_start
print("Done.")

tsv_file = glob.glob(f"{download_dir}/*.tsv.gz")
if len(tsv_file) == link_ct:
    print(f"All {len(tsv_file)} files are downloaded.")
else:
    print(f"{link_ct - len(tsv_file)} files are missing.")

# Took about ~14 minutes to download all 183 files.
print(f"Total time spent for download: {total_time/60} minutes.")
