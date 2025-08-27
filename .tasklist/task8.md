## Phase 8: End-to-End Testing

### Task 8: Implement End-to-End Testing Suite
**Priority**: High | **Estimated Time**: 12 hours

#### Objective
Create comprehensive end-to-end tests that validate complete user workflows, ensuring the entire marketplace functions correctly from a user's perspective.

#### Deliverables
- [ ] User journey tests for major workflows
- [ ] Browser automation tests
- [ ] Performance testing setup
- [ ] Cross-browser compatibility tests
- [ ] Mobile responsiveness validation

#### Implementation Steps

1. **Set Up E2E Testing Framework**
   ```python
   # requirements/testing.txt (additions)
   selenium==4.15.0
   pytest-selenium==4.1.0
   pytest-html==4.0.0
   pytest-xdist==3.3.1
   locust==2.16.1  # For performance testing
   
   # conftest.py (additions for E2E)
   import pytest
   from selenium import webdriver
   from selenium.webdriver.chrome.options import Options
   from django.contrib.staticfiles.testing import StaticLiveServerTestCase
   from django.test import override_settings
   
   @pytest.fixture
   def browser():
       """Set up Chrome browser for testing"""
       chrome_options = Options()
       chrome_options.add_argument("--headless")  # Run in headless mode
       chrome_options.add_argument("--no-sandbox")
       chrome_options.add_argument("--disable-dev-shm-usage")
       
       driver = webdriver.Chrome(options=chrome_options)
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   
   @pytest.fixture
   def live_server():
       """Django live server for E2E testing"""
       from django.test import LiveServerTestCase
       server = LiveServerTestCase()
       server._pre_setup()
       yield server
       server._post_teardown()
   ```

2. **User Registration & Authentication Flow**
   ```python
   # tests/e2e/test_user_authentication.py
   import pytest
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import UserFactory
   
   @pytest.mark.e2e
   class TestUserAuthentication:
       def test_user_registration_complete_flow(self, browser, live_server):
           """Test complete user registration workflow"""
           # Navigate to registration page
           browser.get(f"{live_server.url}/compte/inscription/")
           
           # Fill registration form
           browser.find_element(By.NAME, "first_name").send_keys("Jean")
           browser.find_element(By.NAME, "last_name").send_keys("Dupont")
           browser.find_element(By.NAME, "email").send_keys("jean@example.com")
           browser.find_element(By.NAME, "phone").send_keys("+509 1234-5678")
           browser.find_element(By.NAME, "username").send_keys("jeandupont")
           browser.find_element(By.NAME, "password1").send_keys("SecurePass123!")
           browser.find_element(By.NAME, "password2").send_keys("SecurePass123!")
           
           # Submit form
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Wait for redirect to profile page
           WebDriverWait(browser, 10).until(
               EC.url_contains("/compte/")
           )
           
           # Verify successful registration
           assert "Profil" in browser.title
           welcome_message = browser.find_element(By.CSS_SELECTOR, ".alert-success")
           assert "Compte créé avec succès" in welcome_message.text
       
       def test_user_login_logout_flow(self, browser, live_server):
           """Test user login and logout workflow"""
           # Create test user
           user = UserFactory(username="testuser", email="test@example.com")
           user.set_password("TestPass123!")
           user.save()
           
           # Navigate to login page
           browser.get(f"{live_server.url}/compte/connexion/")
           
           # Fill login form
           browser.find_element(By.NAME, "username").send_keys("testuser")
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Wait for redirect after login
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".user-menu"))
           )
           
           # Verify login success
           user_menu = browser.find_element(By.CSS_SELECTOR, ".user-menu")
           assert user.get_full_name() in user_menu.text
           
           # Test logout
           browser.find_element(By.CSS_SELECTOR, ".logout-btn").click()
           
           # Verify logout
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".login-btn"))
           )
           assert browser.find_element(By.CSS_SELECTOR, ".login-btn")
   ```

3. **Product Browsing & Search Flow**
   ```python
   # tests/e2e/test_product_browsing.py
   import pytest
   from selenium.webdriver.common.by import By
   from selenium.webdriver.common.keys import Keys
   from selenium.webdriver.support.ui import WebDriverWait, Select
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import ProductFactory, CategoryFactory
   
   @pytest.mark.e2e
   class TestProductBrowsing:
       def test_homepage_to_product_detail_flow(self, browser, live_server):
           """Test navigation from homepage to product detail"""
           # Create test products
           category = CategoryFactory(name="Agricole", slug="agricole")
           product = ProductFactory(
               name="Café des Montagnes Bleues",
               category=category,
               is_featured=True
           )
           
           # Navigate to homepage
           browser.get(live_server.url)
           
           # Verify featured products section exists
           featured_section = browser.find_element(By.CSS_SELECTOR, ".featured-products")
           assert featured_section.is_displayed()
           
           # Click on featured product
           product_card = browser.find_element(
               By.CSS_SELECTOR, 
               f"[data-product-id='{product.id}']"
           )
           product_link = product_card.find_element(By.TAG_NAME, "a")
           product_link.click()
           
           # Wait for product detail page
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail"))
           )
           
           # Verify product details
           assert product.name in browser.title
           product_name = browser.find_element(By.CSS_SELECTOR, "h1")
           assert product.name in product_name.text
       
       def test_category_browsing_with_filters(self, browser, live_server):
           """Test category browsing with price filters"""
           category = CategoryFactory(name="Services", slug="services")
           ProductFactory.create_batch(
               5, 
               category=category,
               price__range=(50, 200)
           )
           
           # Navigate to category page
           browser.get(f"{live_server.url}/categorie/services/")
           
           # Apply price filter
           min_price = browser.find_element(By.NAME, "min_price")
           min_price.clear()
           min_price.send_keys("100")
           
           max_price = browser.find_element(By.NAME, "max_price")
           max_price.clear()
           max_price.send_keys("150")
           
           # Apply filter
           filter_btn = browser.find_element(By.CSS_SELECTOR, ".apply-filters")
           filter_btn.click()
           
           # Wait for filtered results
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".product-grid"))
           )
           
           # Verify filtered results
           product_cards = browser.find_elements(By.CSS_SELECTOR, ".product-card")
           for card in product_cards:
               price_element = card.find_element(By.CSS_SELECTOR, ".current-price")
               price_text = price_element.text.replace("HTG", "").strip()
               price_value = float(price_text)
               assert 100 <= price_value <= 150
       
       def test_product_search_functionality(self, browser, live_server):
           """Test product search with results"""
           # Create searchable products
           ProductFactory(name="Café Haïtien Premium", description="Excellent café local")
           ProductFactory(name="Artisanat Traditionnel", description="Art haïtien authentique")
           
           # Navigate to homepage
           browser.get(live_server.url)
           
           # Use search functionality
           search_input = browser.find_element(By.CSS_SELECTOR, "input[name='query']")
           search_input.send_keys("café")
           search_input.send_keys(Keys.RETURN)
           
           # Wait for search results
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results"))
           )
           
           # Verify search results
           results = browser.find_elements(By.CSS_SELECTOR, ".product-card")
           assert len(results) >= 1
           
           # Check that results contain search term
           for result in results:
               product_name = result.find_element(By.CSS_SELECTOR, "h3").text
               assert "café" in product_name.lower()
   ```

4. **Shopping Cart & Checkout Flow**
   ```python
   # tests/e2e/test_shopping_cart.py
   import pytest
   from decimal import Decimal
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import ProductFactory, UserFactory
   
   @pytest.mark.e2e
   class TestShoppingCart:
       def test_complete_purchase_flow(self, browser, live_server):
           """Test complete purchase workflow from product to checkout"""
           # Create test data
           user = UserFactory()
           user.set_password("TestPass123!")
           user.save()
           
           product = ProductFactory(
               name="Test Product",
               price=Decimal('25.00'),
               stock_quantity=10
           )
           
           # Login first
           browser.get(f"{live_server.url}/compte/connexion/")
           browser.find_element(By.NAME, "username").send_keys(user.username)
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Navigate to product detail
           browser.get(f"{live_server.url}/produit/{product.slug}/")
           
           # Add to cart
           qty_input = browser.find_element(By.NAME, "quantity")
           qty_input.clear()
           qty_input.send_keys("2")
           
           add_to_cart_btn = browser.find_element(By.CSS_SELECTOR, ".btn-add-cart")
           add_to_cart_btn.click()
           
           # Wait for cart update confirmation
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
           )
           
           # Navigate to cart
           browser.find_element(By.CSS_SELECTOR, ".cart-btn").click()
           
           # Verify cart contents
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-items"))
           )
           
           cart_item = browser.find_element(By.CSS_SELECTOR, ".cart-item")
           assert product.name in cart_item.text
           
           # Proceed to checkout
           checkout_btn = browser.find_element(By.CSS_SELECTOR, ".btn-checkout")
           checkout_btn.click()
           
           # Fill shipping information
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".checkout-form"))
           )
           
           browser.find_element(By.NAME, "shipping_address").send_keys("123 Rue Test, Port-au-Prince")
           browser.find_element(By.NAME, "shipping_city").send_keys("Port-au-Prince")
           browser.find_element(By.NAME, "shipping_phone").send_keys("+509 1234-5678")
           
           # Continue to payment (mock MonCash for E2E)
           payment_btn = browser.find_element(By.CSS_SELECTOR, ".btn-payment")
           payment_btn.click()
           
           # Verify order creation
           WebDriverWait(browser, 15).until(
               EC.url_contains("/commande/confirmation/")
           )
           
           # Verify order confirmation page
           confirmation_msg = browser.find_element(By.CSS_SELECTOR, ".order-confirmation")
           assert "Commande confirmée" in confirmation_msg.text
       
       def test_cart_quantity_updates(self, browser, live_server):
           """Test cart quantity update functionality"""
           # Setup test data
           user = UserFactory()
           user.set_password("TestPass123!")
           user.save()
           
           product = ProductFactory(stock_quantity=20)
           
           # Login and add product to cart
           self._login_user(browser, live_server, user)
           self._add_product_to_cart(browser, live_server, product, quantity=3)
           
           # Navigate to cart
           browser.get(f"{live_server.url}/panier/")
           
           # Update quantity
           qty_input = browser.find_element(By.CSS_SELECTOR, ".quantity-input input")
           qty_input.clear()
           qty_input.send_keys("5")
           
           update_btn = browser.find_element(By.CSS_SELECTOR, ".update-quantity")
           update_btn.click()
           
           # Wait for quantity update
           WebDriverWait(browser, 10).until(
               EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".quantity-input input"), "5")
           )
           
           # Verify total price updated
           total_element = browser.find_element(By.CSS_SELECTOR, ".cart-total")
           expected_total = float(product.price) * 5
           assert f"{expected_total:.2f}" in total_element.text
       
       def _login_user(self, browser, live_server, user):
           """Helper method to login user"""
           browser.get(f"{live_server.url}/compte/connexion/")
           browser.find_element(By.NAME, "username").send_keys(user.username)
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
       
       def _add_product_to_cart(self, browser, live_server, product, quantity=1):
           """Helper method to add product to cart"""
           browser.get(f"{live_server.url}/produit/{product.slug}/")
           
           qty_input = browser.find_element(By.NAME, "quantity")
           qty_input.clear()
           qty_input.send_keys(str(quantity))
           
           browser.find_element(By.CSS_SELECTOR, ".btn-add-cart").click()
           
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
           )
   ```

5. **Performance Testing Setup**
   ```python
   # tests/performance/locustfile.py
   from locust import HttpUser, task, between
   import random
   
   class MarketplaceUser(HttpUser):
       wait_time = between(1, 3)
       
       def on_start(self):
           """Setup for each simulated user"""
           # Login user for authenticated requests
           self.login()
       
       def login(self):
           """Login user session"""
           response = self.client.get("/compte/connexion/")
           csrf_token = self.extract_csrf_token(response.text)
           
           self.client.post("/compte/connexion/", {
               "username": "testuser",
               "password": "testpass",
               "csrfmiddlewaretoken": csrf_token
           })
       
       @task(3)
       def browse_homepage(self):
           """Browse homepage - most common action"""
           self.client.get("/")
       
       @task(2)
       def browse_categories(self):
           """Browse different categories"""
           categories = ["agricole", "patriotiques", "services", "premiere-necessite"]
           category = random.choice(categories)
           self.client.get(f"/categorie/{category}/")
       
       @task(2)
       def view_products(self):
           """View individual product pages"""
           # This would need actual product slugs from database
           response = self.client.get("/produits/")
           if response.status_code == 200:
               # Extract product URLs from response and visit random ones
               pass
       
       @task(1)
       def search_products(self):
           """Perform product searches"""
           search_terms = ["café", "artisanat", "service", "agriculture"]
           term = random.choice(search_terms)
           self.client.get(f"/recherche/?query={term}")
       
       @task(1)
       def add_to_cart(self):
           """Add items to shopping cart"""
           # This would simulate adding products to cart
           pass
       
       def extract_csrf_token(self, html):
           """Extract CSRF token from HTML"""
           # Simple extraction - in real scenario use proper parsing
           import re
           match = re.search(r'csrf_token.*?value="([^"]*)"', html)
           return match.group(1) if match else ""
   ```

6. **Cross-Browser Testing Configuration**
   ```python
   # tests/e2e/conftest.py (browser fixtures)
   import pytest
   from selenium import webdriver
   from selenium.webdriver.chrome.options import Options as ChromeOptions
   from selenium.webdriver.firefox.options import Options as FirefoxOptions
   
   @pytest.fixture(params=["chrome", "firefox"])
   def multi_browser(request):
       """Test across multiple browsers"""
       if request.param == "chrome":
           chrome_options = ChromeOptions()
           chrome_options.add_argument("--headless")
           driver = webdriver.Chrome(options=chrome_options)
       elif request.param == "firefox":
           firefox_options = FirefoxOptions()
           firefox_options.add_argument("--headless")
           driver = webdriver.Firefox(options=firefox_options)
       
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   
   @pytest.fixture(params=["desktop", "tablet", "mobile"])
   def responsive_browser(request):
       """Test responsive design across device sizes"""
       chrome_options = ChromeOptions()
       chrome_options.add_argument("--headless")
       
       if request.param == "desktop":
           chrome_options.add_argument("--window-size=1920,1080")
       elif request.param == "tablet":
           chrome_options.add_argument("--window-size=768,1024")
       elif request.param == "mobile":
           chrome_options.add_argument("--window-size=375,667")
       
       driver = webdriver.Chrome(options=chrome_options)
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   ```

#### Acceptance Criteria
- [ ] All critical user journeys tested end-to-end
- [ ] Tests run successfully across different browsers
- [ ] Mobile responsiveness validated
- [ ] Performance benchmarks established
- [ ] Automated test execution in CI/CD pipeline

---