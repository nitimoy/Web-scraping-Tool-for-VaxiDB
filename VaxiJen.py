from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def VaxiJen(file_path):

    # Create ChromeOptions object to configure Chrome browser options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')  # Ignore certificate errors
    chrome_options.add_argument(r"--user-data-dir=C:\Users\LeLWa\AppData\Local\Google\Chrome\User Data")

    chrome_options.add_argument(r'--profile-directory=Default')

    # Start the WebDriver with the configured Chrome options
    driver =  uc.Chrome(options=chrome_options)

    # URL of the webpage to be automated
    base_url = 'https://www.ddg-pharmfac.net/vaxijen/VaxiJen/VaxiJen.html'

    # Open the webpage in the Chrome browser
    driver.get(base_url)

    time.sleep(5)

    # Locate the file input element using XPath and send the file path
    file_input = driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr[4]/td[3]/form/table/tbody/tr[1]/td[2]/p/input')
    file_input.send_keys(file_path)

    # Locate the dropdown element for selecting the target organism
    dropdown_element = driver.find_element(By.NAME, 'Target')

    # Create a Select object using the dropdown element
    dropdown = Select(dropdown_element)

    # Select the desired option ('Bacteria') from the dropdown
    dropdown.select_by_visible_text('Parasite')

    # Locate the Threshold input box element
    threshold_input = driver.find_element(By.NAME, 'threshold')

    # Clear any existing value in the Threshold input box
    threshold_input.clear()

    # Send the desired value ('0.4') to the Threshold input box
    threshold_input.send_keys('0.4')

    # Locate and click the submit button using XPath
    submit_button = driver.find_element(By.XPATH, '/html/body/div[1]/table/tbody/tr[4]/td[3]/form/table/tbody/tr[3]/td[2]/input[1]')
    submit_button.click()

    results_element = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/table/tbody/tr[4]/td[3]/table/tbody/tr/td"))
    )
    time.sleep(5)
    # Extract the text from the results element, strip any leading/trailing whitespace, and split the text into lines
    predictions = results_element.text.strip().splitlines()

    # Create a list to store the extracted data
    data_list = []

    # Iterate through each prediction line
    for i in range(len(predictions)):
        current_line = predictions[i]
        if current_line.startswith(">"):  # Check if the line starts with ">tr|", indicating a Protein ID
            # Extract Protein ID from the current line
            Protein_ID = current_line.split("|")[1]
            
            # Find the next line containing "Overall Prediction" after the Protein ID line
            next_prediction_line = None
            for j in range(i + 1, len(predictions)):
                if "Overall Prediction" in predictions[j]:
                    # Extract only the prediction part from the line
                    next_prediction_line = predictions[j].split("=")[1].strip()
                    break

            # If a prediction line is found, extract relevant information and print
            if next_prediction_line:
                # Split the protein description by whitespaces (assuming space separated)
                protein_description_parts = predictions[i].split("|")
                protein_name = protein_description_parts[2].split("OS")[0]  # Extract protein name
                antigenic_score = next_prediction_line.split()[0]  # Extract antigenic score (first element in prediction line)
                probable = next_prediction_line.split()[3]  # Extract probability

                # Create a dictionary for the current row of data
                data_dict = {
                    'Protein_ID': Protein_ID,
                    'Protein_Name': protein_name,
                    'Antigenic_Score': antigenic_score,
                    'Probable': probable
                }

                # Append the dictionary to the data list
                data_list.append(data_dict)

    # Create a DataFrame from the data list
    df = pd.DataFrame(data_list)

    # Quit the WebDriver
    driver.quit()

    return df
