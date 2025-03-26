import os
import time

import django
from channels.auth import login

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from .selenium_utils import sel_login


from app.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_tutors.settings")
django.setup()


class TestLogInPage(StaticLiveServerTestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            email_address='tutor@example.com',
            password='Safepassword123',
            role=User.TUTOR,
            first_name='Jane',
            last_name='Doe'
        )
        self.student = User.objects.create_user(
            email_address='student@example.com',
            password='Safepassword123',
            role=User.STUDENT,
            first_name='John',
            last_name='Doe'
        )

        self.driver = webdriver.Chrome()
        self.tutor_url = f"{self.live_server_url}/tutor-dashboard/"
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.quit()


    def test_logged_out_navbar(self):
        self.driver.get(f"{self.live_server_url}")


        self.driver.find_element(By.LINK_TEXT, 'About Us').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/about_us/")

        self.driver.find_element(By.LINK_TEXT, 'Login').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/login/")

        self.driver.find_element(By.LINK_TEXT, 'Sign Up').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/sign-up/")

        self.driver.find_element(By.LINK_TEXT, 'Home').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")

    def test_tutor_navbar(self):
        sel_login(self.driver, self.tutor.email_address, 'Safepassword123', self.live_server_url)
        self.driver.get(self.tutor_url)
        self.driver.maximize_window()

        self.driver.find_element(By.LINK_TEXT, 'Dashboard').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/tutor-dashboard/")

        self.driver.find_element(By.LINK_TEXT, 'Your Quizzes').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/your-quizzes/")

        self.driver.find_element(By.LINK_TEXT, 'Classrooms').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/tutor-classrooms/")

        self.driver.find_element(By.LINK_TEXT, 'Stats').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/tutor-stats/")

        self.driver.find_element(By.LINK_TEXT, 'Profile').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/tutor-profile/")

        self.driver.find_element(By.LINK_TEXT, 'Logout').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/login/")
        self.assertTrue("Logged out successfully!" in self.driver.page_source)

    def test_student_navbar(self):
        sel_login(self.driver, self.student.email_address, 'Safepassword123', self.live_server_url)
        self.driver.find_element(By.LINK_TEXT, 'Dashboard').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/student-dashboard/")

        self.driver.find_element(By.LINK_TEXT, 'Classrooms').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/student-classrooms/")

        self.driver.find_element(By.LINK_TEXT, 'Profile').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/student-profile/")

        self.driver.find_element(By.LINK_TEXT, 'Stats').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/student/{self.student.id}/stats/")

        self.driver.find_element(By.LINK_TEXT, 'Join Room').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/join-quiz/")

        self.driver.find_element(By.LINK_TEXT, 'Logout').click()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/login/")









