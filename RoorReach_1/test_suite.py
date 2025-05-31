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
    """Test suite for RoorReach authentication functionality and cart operations"""
    
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
            # Navigate to login page first
            self.driver.get("http://127.0.0.1:8000/login/")
            
            # Login process
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.send_keys("BBuyer")
            
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.click()
            password_field.send_keys("Test@1234")
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn:nth-child(4)")))
            login_button.click()
            
            # Wait for login redirect
            self.wait.until(EC.url_changes("http://127.0.0.1:8000/login/"))
            
            # Find and click Add to Cart button
            add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add to Cart")))
            add_to_cart_button.click()
            
            # Wait and click Proceed to Checkout
            checkout_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Proceed to Checkout")))
            checkout_button.click()
            
            # Fill checkout form
            self.wait.until(EC.presence_of_element_located((By.ID, "full_name"))).send_keys("Akhi")
            self.wait.until(EC.presence_of_element_located((By.ID, "phone"))).send_keys("01757499561")
            self.wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("afrin@1234gmail.com")
            self.wait.until(EC.presence_of_element_located((By.ID, "shipping_address"))).send_keys("df")
              # Take screenshot of successful checkout form completion
            self.driver.save_screenshot("checkout_success.png")
            
            print("Test passed: Successfully filled checkout form with user details")
            
            # Test ends here after filling checkout form
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("order_failure.png")
            raise e

    def test_4_about_page(self):
        """Test about page navigation"""
        try:
            # Navigate to home page
            self.driver.get("http://127.0.0.1:8000/")
            
            # Find and click About Us link
            about_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "About Us")))
            about_link.click()
            
            # Verify we are on about page
            self.wait.until(EC.url_contains("/about"))
            current_url = self.driver.current_url
            assert "about" in current_url.lower(), "Navigation to About page failed"
            
            # Take screenshot of successful about page navigation
            self.driver.save_screenshot("about_page_success.png")
            
            print("Test passed: Successfully navigated to About Us page")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("about_page_failure.png")
            raise e

    def test_5_policy_page(self):
        """Test policy page navigation"""
        try:
            # Navigate directly to policies page
            self.driver.get("http://127.0.0.1:8000/policies/")
            
            # Verify we are on policy page
            current_url = self.driver.current_url
            assert "policies" in current_url.lower(), "Navigation to Policy page failed"
            
            # Verify the page loaded by checking for policy header
            policy_header = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "policy-header")))
            assert policy_header is not None, "Policy header not found"
            
            # Take screenshot of successful policy page navigation
            self.driver.save_screenshot("policy_page_success.png")
            
            print("Test passed: Successfully navigated to Policies page")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("policy_page_failure.png")
            raise e

    def test_6_terms_page(self):
        """Test terms and conditions page navigation and content"""
        try:
            # Navigate directly to terms page
            self.driver.get("http://127.0.0.1:8000/terms-conditions/")
            
            # Verify we are on terms page
            current_url = self.driver.current_url
            assert "terms-conditions" in current_url.lower(), "Navigation to Terms & Conditions page failed"
            
            # Verify page sections are present and clickable
            sections = [
                (By.CSS_SELECTOR, ".section-card:nth-child(1) > h3"),
                (By.CSS_SELECTOR, ".section-card:nth-child(3) > p"),
                (By.CSS_SELECTOR, ".section-card:nth-child(5) > p"),
                (By.CSS_SELECTOR, ".section-card:nth-child(7) > p")
            ]
            
            # Check each section
            for locator in sections:
                element = self.wait.until(EC.presence_of_element_located(locator))
                assert element is not None, f"Section {locator[1]} not found"
                element.click()
            
            # Take screenshot of successful terms page navigation
            self.driver.save_screenshot("terms_page_success.png")
            
            print("Test passed: Successfully navigated to Terms & Conditions page and verified content")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("terms_page_failure.png")
            raise e

    def test_7_search_functionality(self):
        """Test search functionality"""
        try:
            # Navigate to home page
            self.driver.get("http://127.0.0.1:8000/")
            
            # Find and click search field
            search_field = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_field.click()
            
            # Enter search term
            search_term = "zuta"
            search_field.send_keys(search_term)
            search_field.send_keys(Keys.ENTER)
            
            # Verify we are on search results page
            self.wait.until(EC.url_contains("/search/"))
            current_url = self.driver.current_url
            assert "search" in current_url.lower(), "Navigation to search results failed"
            assert search_term in current_url, f"Search term '{search_term}' not found in URL"
            
            # Take screenshot of search results
            self.driver.save_screenshot("search_results_success.png")
            
            print(f"Test passed: Successfully performed search for '{search_term}'")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("search_failure.png")
            raise e

    def test_8_category_navigation(self):
        """Test category navigation and search"""
        try:
            # Navigate to home page
            self.driver.get("http://127.0.0.1:8000/")
            
            # Find and click View All Categories link
            categories_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "View All Categories")))
            categories_link.click()
            
            # Verify we are on categories page
            self.wait.until(EC.url_contains("/categories"))
            
            # Find and interact with category search
            search_field = self.wait.until(EC.presence_of_element_located((By.NAME, "search")))
            search_field.click()
            search_field.send_keys("food")
            
            # Click search button
            search_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-button")))
            search_button.click()
            
            # Wait for and click on a category card
            category_card = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".category-card")))
            category_card.click()
            
            # Take screenshot of successful category navigation
            self.driver.save_screenshot("category_navigation_success.png")
            
            print("Test passed: Successfully navigated categories and performed category search")
            
        except Exception as e:
            # Take screenshot of failure
            self.driver.save_screenshot("category_navigation_failure.png")
            raise e
