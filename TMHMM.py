from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def TMHMM(file_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=chrome_options)

    base_url = 'https://services.healthtech.dtu.dk/services/TMHMM-2.0/'

    driver.get(base_url)

    time.sleep(5)

    '''cookie_consent_element = driver.find_element(By.ID, "cookiescript_injected")
    if cookie_consent_element.is_displayed():
        cookie_consent_button = driver.find_element(By.ID, "cookiescript_accept")
        cookie_consent_button.click()'''

    time.sleep(5)

    file_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="file"]'))
    )
    file_input.send_keys(file_path)

    radio_button = driver.find_element(By.XPATH, '//input[@name="outform" and @value="-noplot"]')

    if not radio_button.is_selected():
        radio_button.click()

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))
    )
    submit_button.click()

    pre_element = WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.TAG_NAME, 'pre'))
    )
    time.sleep(5)

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all <pre> tags
    pre_tags = soup.find_all('pre')

    results = []

    # Extract the desired information from each <pre> tag
    for pre_tag in pre_tags:
        lines = pre_tag.get_text().split('\n')
        for line in lines:
            if "predicted TMHs:" in line:
                output = line.strip()
                output_lines = output.split('\n')

                # Extract ProteinID and X from each line
                for line in output_lines:
                    if line.strip():  # Check if the line is not empty
                        parts = line.split()
                        protein_id = parts[1].split('|')[1]  # Extract ProteinID from the second part of the line
                        x_value = parts[-1]  # Extract X (number of predicted TMHs) from the last part of the line
                        results.append({'Protein_ID': protein_id, 'TMHs': x_value})

    df = pd.DataFrame(results)

    # Quit the WebDriver
    driver.quit()

    return df
