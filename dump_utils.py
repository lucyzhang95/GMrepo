from selenium.webdriver.common.by import By
import time

def get_project_links(driver, wait):
    """
    Get all project groups on the current page.

    :param driver: Selenium webdriver
    :param wait: Webdriver wait time
    :return: a dictionary mapping project id to list of phenotype links.
    """
    project_links = {}
    groups_data = []
    group_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'ng-table-group')]")
    for i, group in enumerate(group_rows):
        try:
            proj_text = group.find_element(By.CSS_SELECTOR, "strong.ng-binding").text
            proj_id = proj_text.split()[0].strip()
            groups_data.append((i, proj_id))
        except Exception as e:
            print(f"Could not extract project text at index {i}: {e}")

    for idx, proj_id in groups_data:
        try:
            group = driver.find_elements(By.XPATH, "//tr[contains(@class, 'ng-table-group')]")[idx]
            time.sleep(1)

            script = """
                var groupRow = arguments[0];
                var siblings = [];
                var next = groupRow.nextElementSibling;
                var counter = 0;
                while(next && !next.classList.contains('ng-table-group') && counter < 50){
                    siblings.push(next);
                    next = next.nextElementSibling;
                    counter++;
                }
                return siblings;
            """
            sibling_rows = driver.execute_script(script, group)

            links = []
            for row in sibling_rows:
                try:
                    link = row.find_element(By.XPATH, ".//a[starts-with(@href, '/phenotypes/')]")
                    href = link.get_attribute("href")
                    if href:
                        print(f"Found link: {href}")
                        links.append(href)
                except Exception:
                    continue
            if links:
                project_links[proj_id] = links
        except Exception as e:
            print(f"Error processing project {proj_id} at index {idx}: {e}")
    return project_links
