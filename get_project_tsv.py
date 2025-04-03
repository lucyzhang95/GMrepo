from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

# TODO: haven't tested yet, get stuck after opening chrome browser
# get project ids and hrefs per phenotype/disease under that project
project_links = {}

groups_data = []
group_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'ng-table-group')]")
for i, group in enumerate(group_rows):
    try:
        proj_text = group.find_element(By.CSS_SELECTOR, "strong.ng-binding").text
        proj_id = proj_text.split()[0].strip()
        groups_data.append((i, proj_id))
    except Exception as e:
        print(f"Could not find {proj_text} at index {i}: {e}")

for idx, proj_id in groups_data:
    try:
        group = driver.find_elements(By.XPATH, "//tr[contains(@class, 'ng-table-group')]")[index]
        time.sleep(1)

        script = """
        var groupRow = arguments[0];
        var siblings = [];
        var next = groupRow.nextElementSibling;
        while(next && !next.classList.contains('ng-table-group')){
            siblings.push(next);
            next = next.nextElementSibling;
        }
        return siblings;
        """
        sibling_rows = driver.execute_script(script, group)

        # get href links per each phenotype
        links = []
        for row in sibling_rows:
            try:
                link = row.find_element(By.XPATH, ".//a[starts-with(@href, '/phenotypes/')]")
                href = link.get_attribute("href")
                if href:
                    print(f"Found link: {href}")
                    links.append(href)
            except Exception as e:
                continue

        if links:
            project_links[proj_id] = links
    except Exception as e:
        print(f"Error processing project {proj_id} at index {idx}: {e}")

link_ct = sum([len(link) for link in project_links.values()])
print(f"Found {len(project_links)} projects.")
print(f"Found {link_ct} links.")
