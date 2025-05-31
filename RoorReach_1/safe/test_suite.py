import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestRoorReachAuth():
    """Test suite for RoorReach authentication functionality"""
    
    def setup_method(self, method):
        """Set up test environment before each test method"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        service = Service('chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.vars = {}

    def teardown_method(self, method):
        """Clean up after each test method"""
        if self.driver:
            self.driver.quit()

    def test_1_signup(self):
        """Test user registration functionality"""
        try:
            # Navigate to register page
            self.driver.get("http://127.0.0.1:8000/register")
            
            # Fill in registration form
            self.wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys("Testt")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_first_name"))).send_keys("t")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_last_name"))).send_keys("t")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_email"))).send_keys("Test@gmail.com")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_phone"))).send_keys("01757499561")
            
            # Handle gender dropdown
            gender_dropdown = self.wait.until(EC.presence_of_element_located((By.ID, "id_gender")))
            gender_dropdown.click()
            gender_option = self.wait.until(EC.presence_of_element_located((By.XPATH, "//option[. = 'Female']")))
            gender_option.click()
            
            # Fill remaining fields
            self.wait.until(EC.presence_of_element_located((By.ID, "id_location"))).send_keys("Jessore")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_address"))).send_keys("ddfdsf")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_password1"))).send_keys("Test@1234")
            self.wait.until(EC.presence_of_element_located((By.ID, "id_password2"))).send_keys("Test@1234")
            
            # Submit registration form
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn:nth-child(12)")))
            submit_button.click()
              # Verify successful registration and redirection to homepage
            self.wait.until(EC.url_changes("http://127.0.0.1:8000/register"))
            current_url = self.driver.current_url
            assert current_url.endswith("/") or "home" in current_url.lower(), "Registration failed - not redirected to homepage"
            
            # Take screenshot of successful registration
            self.driver.save_screenshot("signup_success.png")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("signup_failure.png")
            raise e

    def test_2_login(self):
        """Test user login functionality"""
        try:
            # Navigate to login page
            self.driver.get("http://127.0.0.1:8000/login/")
            
            # Wait for and fill username
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.click()
            username_field.send_keys("BBuyer")
            
            # Wait for and fill password
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.click()
            password_field.send_keys("Test@1234")
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn:nth-child(4)")))
            login_button.click()

            # Wait for redirect and verify we're no longer on login page
            self.wait.until(EC.url_changes("http://127.0.0.1:8000/login/"))
            current_url = self.driver.current_url
            assert "login" not in current_url.lower(), "Login failed - still on login page"
            
            # Take screenshot of successful login
            self.driver.save_screenshot("login_success.png")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("login_failure.png")
            raise e

    def test_3_add_to_cart_and_checkout(self):
        """Test adding product to cart and completing checkout process"""
        try:
            # Login first (reusing login functionality)
            self.test_2_login()
            print("✅ Logged in successfully")
            
            # Find and click Add to Cart button
            add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add to Cart")))
            add_to_cart_button.click()
            print("✅ Added item to cart")
            
            # Wait and click Proceed to Checkout
            checkout_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Proceed to Checkout")))
            checkout_button.click()
            print("✅ Proceeded to checkout")
            
            # Fill checkout form
            self.wait.until(EC.presence_of_element_located((By.ID, "full_name"))).send_keys("Test User")
            self.wait.until(EC.presence_of_element_located((By.ID, "phone"))).send_keys("01757499561")
            self.wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("test@gmail.com")
            self.wait.until(EC.presence_of_element_located((By.ID, "shipping_address"))).send_keys("Test Address")
            print("✅ Filled checkout form")
            
            # Submit order
            place_order_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".place-order-btn")))
            place_order_button.click()
            print("✅ Placed order")
            
            # Verify order placement
            time.sleep(2)  # Wait for order processing
            success_message = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success")))
            assert "order" in success_message.text.lower(), "Order placement failed"
            
            # Navigate to order page
            self.driver.get("http://127.0.0.1:8000/orders/")
            print("✅ Navigated to orders page")
            
            # Verify order appears in order history
            order_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".order-item")))
            assert order_element is not None, "Order not found in order history"
            
            # Take screenshot of order confirmation
            self.driver.save_screenshot("order_success.png")
            print("✅ Order process completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.driver.save_screenshot("order_failure.png")
            raise e
