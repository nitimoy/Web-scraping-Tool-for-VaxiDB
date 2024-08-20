from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import requests
import re

def SignalP(file_path):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=chrome_options)

    base_url = 'https://services.healthtech.dtu.dk/services/SignalP-5.0/'

    driver.get(base_url)

    '''cookie_consent_element = driver.find_element(By.ID, "cookiescript_injected")
    if cookie_consent_element.is_displayed():
        cookie_consent_button = driver.find_element(By.ID, "cookiescript_accept")
        cookie_consent_button.click()'''

    time.sleep(5)

    file_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="file"]'))
    )

    file_input.send_keys(file_path)

    radio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@name="format" and @value="short"]'))
    )
    time.sleep(3)

    if not radio_button.is_selected():
        ActionChains(driver).move_to_element(radio_button).click().perform()
        radio_button.click()

    time.sleep(4)

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))
    )
    driver.execute_script("arguments[0].click();", submit_button)

    row_element = WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.CLASS_NAME, "row"))
    )
    # Wait for the element to be present and clickable
    json_summary_link = WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "JSON Summary")]'))
    )

    # Get the href attribute of the JSON Summary link
    json_url = json_summary_link.get_attribute("href")

    response = requests.get(json_url)

    if response.status_code == 200:
        # Decode the JSON content from the response
        parsed_json = response.json()
        sequences = parsed_json.get("SEQUENCES", {})

        # List to store extracted data
        extracted_data = []

        for details in sequences.values():
            name = re.search(r'_(.*?)_', details['Name']).group(1)
            prediction = details.get("Prediction", "")
            extracted_data.append({"Protein_ID": name, "Prediction": prediction})

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(extracted_data)
        
        return df

    driver.quit()
