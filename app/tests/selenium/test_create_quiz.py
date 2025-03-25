import os
import re
import time

import django
from channels.auth import login

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from .selenium_utils import sel_login


from app.models import User, Quiz, IntegerInputQuestion, TextInputQuestion

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

        self.driver = webdriver.Chrome()
        self.tutor_url = f"{self.live_server_url}/tutor-dashboard/"
        self.driver.implicitly_wait(3)

    def tearDown(self):
        self.driver.quit()

    def test_create_quiz(self):
        sel_login(self.driver, self.tutor.email_address, "Safepassword123", self.live_server_url)
        self.driver.get(f"{self.live_server_url}/create-quiz/")
        self.driver.find_element(By.NAME, 'name').send_keys('Sample Quiz Name')
        self.driver.find_element(By.NAME, 'subject').send_keys('Math')
        self.driver.find_element(By.NAME, 'difficulty').send_keys('Easy')
        self.driver.find_element(By.NAME, 'is_public').click()
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertTrue(Quiz.objects.count() > 0)
        self.assertTrue(re.match(rf"{self.live_server_url}/edit-quiz/\d+/", self.driver.current_url))


    def test_create_invalid_quiz(self):
        sel_login(self.driver, self.tutor.email_address, "Safepassword123", self.live_server_url)
        self.driver.get(f"{self.live_server_url}/create-quiz/")
        self.driver.find_element(By.NAME, 'name').send_keys('')
        self.driver.find_element(By.NAME, 'subject').send_keys('Math')
        self.driver.find_element(By.NAME, 'difficulty').send_keys('Easy')
        self.driver.find_element(By.NAME, 'is_public').click()
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        self.assertTrue(Quiz.objects.count() == 0)
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/create-quiz/")
        error_container = self.driver.find_element(By.CLASS_NAME, 'form-error-container')
        self.assertTrue(error_container.is_displayed(), "Error container is not displayed")

    def test_create_questions(self):
        self.test_create_quiz()

        def create_question(question_type, question_data):
            question = self.driver.find_element(By.XPATH, f"//div[@data-type='{question_type}']")
            drop_area = self.driver.find_element(By.ID, "editor")
            actions = ActionChains(self.driver)
            actions.drag_and_drop(question, drop_area).perform()

            self.driver.find_element(By.NAME, "time").send_keys(question_data['time'])
            self.driver.find_element(By.NAME, "mark").send_keys(question_data['mark'])
            self.driver.find_element(By.NAME, "correct_answer").send_keys(question_data['correct_answer'])
            self.driver.find_element(By.NAME, "question_text").send_keys(question_data['question_text'])
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        create_question('integer',
                {'time': '30', 'mark': '5', 'correct_answer': '10', 'question_text': 'What is 5 + 5?'})
        self.assertEqual(IntegerInputQuestion.objects.count(), 1)

        create_question('text', {'time': '30', 'mark': '5', 'correct_answer': 'amswerop',
                                 'question_text': 'Enter answer?'})
        self.assertEqual(TextInputQuestion.objects.count(), 1)




