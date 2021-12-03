"""Report tests."""

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.ui import WebDriverWait


class element_has_no_css_class:
    """An expectation for checking that an element has no css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return element if len(element.get_attribute("class")) == 0 else False


class nr_elements:
    """An expectation for the number of matching elements."""

    def __init__(self, locator, expected_nr: int):
        self.locator = locator
        self.expected_nr = expected_nr

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        return elements if len(elements) == self.expected_nr else False


class OpenReportTest(unittest.TestCase):
    """Open a report."""

    def setUp(self):
        """Override to setup the driver."""
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Remote("http://selenium:4444", options=firefox_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get("http://www:80")

    def tearDown(self):
        """Override to close the driver."""
        self.driver.quit()

    def login(self):
        """Login a user."""
        self.driver.find_element(By.XPATH, '//button[text()="Login"]').click()
        login_form = self.driver.find_element(By.CLASS_NAME, "form")
        login_form.find_element(By.NAME, "username").send_keys("jadoe")
        login_form.find_element(By.NAME, "password").send_keys("secret")
        login_form.find_element(By.CLASS_NAME, "button").click()
        self.wait.until(element_has_no_css_class((By.TAG_NAME, "body")))  # Wait for body dimmer to disappear

    def test_title(self):
        """Test the title."""
        self.assertTrue(expect.title_contains("Quality-time"))

    def test_open_report(self):
        """Test that the first report can be opened."""
        report = self.driver.find_elements(By.CLASS_NAME, "card")[0]
        report_title = report.find_element(By.CLASS_NAME, "header")
        report.click()
        self.assertTrue(
            expect.text_to_be_present_in_element(self.driver.find_element(By.CLASS_NAME, "header"), report_title)
        )

    def test_login_and_logout(self):
        """Test that a user can login and logout."""
        self.login()
        logout_dropdown = self.driver.find_element(By.CLASS_NAME, "dropdown")
        logout_dropdown.click()
        logout_menu_item = self.driver.find_element(By.CLASS_NAME, "selected.item")
        logout_menu_item.click()
        self.assertTrue(self.driver.find_element(By.XPATH, '//button[text()="Login"]'))

    def test_add_report(self):
        """Test that a logged in user can add a report."""
        self.login()
        nr_reports = len(self.driver.find_elements(By.CLASS_NAME, "card"))
        self.driver.find_element(By.CLASS_NAME, "button.primary").click()
        self.wait.until(nr_elements((By.CLASS_NAME, "card"), nr_reports + 1))
