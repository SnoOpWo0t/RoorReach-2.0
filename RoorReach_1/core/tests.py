from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from .models import CustomUser, Category, Product
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RootReachTest(LiveServerTestCase):
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Run in headless mode
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.browser.implicitly_wait(10)
        logger.info('Setting up test browser...')
        
        # Create test user for login tests
        self.test_username = 'testuser'
        self.test_password = 'testpassword123'
        self.test_email = 'test@example.com'
        self.test_user = CustomUser.objects.create_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        
    def tearDown(self):
        self.browser.quit()
        logger.info('Tearing down test browser...')

    def test_register_new_user(self):
        """Test user registration functionality"""
        try:
            # Navigate to register page
            self.browser.get(f'{self.live_server_url}/register/')
            logger.info('Navigated to register page')

            # Fill in the registration form
            username_input = self.browser.find_element(By.NAME, 'username')
            email_input = self.browser.find_element(By.NAME, 'email')
            password1_input = self.browser.find_element(By.NAME, 'password1')
            password2_input = self.browser.find_element(By.NAME, 'password2')

            username_input.send_keys('newuser')
            email_input.send_keys('newuser@example.com')
            password1_input.send_keys('securepass123')
            password2_input.send_keys('securepass123')

            # Submit the form
            self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            logger.info('Submitted registration form')

            # Wait for redirect to home page after successful registration
            WebDriverWait(self.browser, 10).until(
                EC.url_to_be(f'{self.live_server_url}/')
            )
            
            # Verify registration was successful
            self.assertEqual(self.browser.current_url, f'{self.live_server_url}/')
            logger.info('Registration successful')

        except TimeoutException:
            logger.error('Timeout waiting for registration to complete')
            raise
        except Exception as e:
            logger.error(f'Error during registration test: {str(e)}')
            raise

    def test_login_and_logout(self):
        """Test login and logout functionality"""
        try:
            # Test Login
            self.browser.get(f'{self.live_server_url}/login/')
            logger.info('Navigated to login page')

            # Fill in login form
            username_input = self.browser.find_element(By.NAME, 'username')
            password_input = self.browser.find_element(By.NAME, 'password')

            username_input.send_keys(self.test_username)
            password_input.send_keys(self.test_password)

            # Submit login form
            self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            logger.info('Submitted login form')

            # Wait for redirect to home page after successful login
            WebDriverWait(self.browser, 10).until(
                EC.url_to_be(f'{self.live_server_url}/')
            )
            
            # Verify login was successful
            self.assertEqual(self.browser.current_url, f'{self.live_server_url}/')
            logger.info('Login successful')

            # Test Logout
            logout_link = self.browser.find_element(By.CSS_SELECTOR, 'a[href="/logout/"]')
            logout_link.click()
            logger.info('Clicked logout link')

            # Wait for redirect to login page after logout
            WebDriverWait(self.browser, 10).until(
                EC.url_to_be(f'{self.live_server_url}/login/')
            )
            
            # Verify logout was successful
            self.assertEqual(self.browser.current_url, f'{self.live_server_url}/login/')
            logger.info('Logout successful')

        except TimeoutException:
            logger.error('Timeout waiting for login/logout operation')
            raise
        except Exception as e:
            logger.error(f'Error during login/logout test: {str(e)}')
            raise