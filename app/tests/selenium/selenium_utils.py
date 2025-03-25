import os
import django
from selenium import webdriver
from selenium.webdriver.common.by import By

# Make sure to set up Django environment properly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_tutors.settings")
django.setup()

def sel_login(driver, email, password, live_server_url):
    driver.get(f"{live_server_url}/login/")
    driver.find_element(By.NAME, 'email_address').send_keys(email)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
