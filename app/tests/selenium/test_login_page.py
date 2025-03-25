import os
import django

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

from app.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_tutors.settings")
django.setup()


class TestLogInPage(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.url = f"{self.live_server_url}/login/"
        self.driver.get(self.url)
        self.input = {}
        self.driver.implicitly_wait(3)
        self.student = User.objects.create_user(
            email_address='student@example.com',
            password='Safepassword123',
            role=User.STUDENT,
            first_name='John',
            last_name='Doe'
        )
        self.tutor = User.objects.create_user(
            email_address='tutor@example.com',
            password='Safepassword123',
            role=User.TUTOR,
            first_name='Jane',
            last_name='Doe'
        )


    def tearDown(self):
        self.driver.quit()

    def test_tutor_login(self):
        self.driver.find_element(By.NAME, 'email_address').send_keys(self.tutor.email_address)
        self.driver.find_element(By.NAME, 'password').send_keys('Safepassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/tutor-dashboard/")

    def test_student_login(self):
        self.driver.find_element(By.NAME, 'email_address').send_keys(self.student.email_address)
        self.driver.find_element(By.NAME, 'password').send_keys('Safepassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/student-dashboard/")

    def test_invalid_login(self):
        self.driver.find_element(By.NAME, 'email_address').send_keys('not_real@email.com')
        self.driver.find_element(By.NAME, 'password').send_keys('Safepassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertEqual(self.driver.current_url, self.url)

    def test_blank_login(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertEqual(self.driver.current_url, self.url)





