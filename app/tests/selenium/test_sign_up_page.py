import os
import django

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_tutors.settings")
django.setup()


class TestSignUpPage(StaticLiveServerTestCase):
    def setUp(self):
        # self.driver = webdriver.Chrome(
        #     service=Service(ChromeDriverManager().install()))
        self.driver = webdriver.Chrome()
        self.url = f"{self.live_server_url}/sign-up/"
        self.driver.get(self.url)
        self.input = {}
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.quit()

    def test_valid_tutor_signup(self):
        self.driver.get(self.url)

        self.driver.find_element(By.NAME, 'first_name').send_keys('John')
        self.driver.find_element(By.NAME, 'last_name').send_keys('Doe')
        self.driver.find_element(By.NAME, 'email_address').send_keys('johndoe@example.com')
        self.driver.find_element(By.NAME, 'role').send_keys('Tutor')
        self.driver.find_element(By.NAME, 'password1').send_keys('SecurePassword123')
        self.driver.find_element(By.NAME, 'password2').send_keys('SecurePassword123')

        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        expected_url = f"{self.live_server_url}/tutor-dashboard/"
        self.assertEqual(self.driver.current_url, expected_url)

    def test_valid_student_signup(self):
        self.driver.get(self.url)

        self.driver.find_element(By.NAME, 'first_name').send_keys('John')
        self.driver.find_element(By.NAME, 'last_name').send_keys('Doe')
        self.driver.find_element(By.NAME, 'email_address').send_keys('johndoe@example.com')
        self.driver.find_element(By.NAME, 'role').send_keys('Student')
        self.driver.find_element(By.NAME, 'password1').send_keys('SecurePassword123')
        self.driver.find_element(By.NAME, 'password2').send_keys('SecurePassword123')

        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        expected_url = f"{self.live_server_url}/student-dashboard/"
        self.assertEqual(self.driver.current_url, expected_url)

    def test_invalid_signup(self):
        self.driver.get(f"{self.live_server_url}/sign-up/")

        self.driver.find_element(By.NAME, 'first_name').send_keys('John')
        self.driver.find_element(By.NAME, 'last_name').send_keys('Doe')
        self.driver.find_element(By.NAME, 'email_address').send_keys('johndoe@example.com')
        self.driver.find_element(By.NAME, 'role').send_keys('Tutor')
        self.driver.find_element(By.NAME, 'password1').send_keys('SecurePassword123')
        self.driver.find_element(By.NAME, 'password2').send_keys('SecurePassword12')

        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertEqual(self.driver.current_url, self.url)

