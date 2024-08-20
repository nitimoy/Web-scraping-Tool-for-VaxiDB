from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from io import BytesIO
import requests
import time
import pandas as pd

def DeepLoc(file_path):
    # Create ChromeOptions object
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=chrome_options)

    # URL of the webpage
    base_url = 'https://services.healthtech.dtu.dk/services/DeepLoc-2.0/'

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

    radio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@name="format" and @value="short"]'))
    )

    time.sleep(3)

    if not radio_button.is_selected():
        ActionChains(driver).move_to_element(radio_button).click().perform()
        radio_button.click()

    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))
    )
    driver.execute_script("arguments[0].click();", submit_button)

    def wait_for_title(driver, title, timeout=600):
        WebDriverWait(driver, timeout).until(
            EC.title_contains(title)
        )


    wait_for_title(driver, "DeepLoc-2.0")

    csv_summary_link = WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "CSV Summary")]'))
    ) 

    time.sleep(10)

    csv_url = csv_summary_link.get_attribute("href")

    response = requests.get(csv_url)

    csv_content = BytesIO(response.content)

    # Read the CSV file directly into a pandas DataFrame from the URL
    df = pd.read_csv(csv_content)

    # Extract the text between the first and second underscores for each row
    extracted_text = df['Protein_ID'].str.split('_', expand=True)[1]

    # Update the "Protein_ID" column with the extracted text
    df['Protein_ID'] = extracted_text

    driver.quit()
    return df