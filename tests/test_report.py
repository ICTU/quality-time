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
        chrome_options = webdriver.ChromeOptions()
        for argument in "headless no-sandbox single-process disable-dev-shm-usage disable-gpu".split(" "):
            chrome_options.add_argument(f"--{argument}")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get("http://www:80")

    def tearDown(self):
        self.driver.close()

    def login(self):
        """Login the default admin user."""
        self.driver.find_element_by_class_name("button").click()
        login_form = self.driver.find_element_by_class_name("form")
        login_form.find_element_by_name("username").send_keys("admin")
        login_form.find_element_by_name("password").send_keys("admin")
        login_form.find_element_by_class_name("button").click()
        self.wait.until(element_has_no_css_class((By.TAG_NAME, "body")))  # Wait for body dimmer to disappear

    def assert_text_to_be_present_in_element(self, element, text: str):
        """Assert that the text is present in the element."""
        self.assertTrue(expect.text_to_be_present_in_element(element, text))

    def test_title(self):
        """Test the title."""
        self.assertTrue(expect.title_contains("Quality-time"))

    def test_login_and_logout(self):
        """Test that the admin user can login and logout."""
        self.login()
        logout_button = self.driver.find_element_by_class_name("button")
        self.assert_text_to_be_present_in_element(logout_button, "Logout admin")
        logout_button.click()
        self.assert_text_to_be_present_in_element(logout_button, "Login")

    def test_add_open_and_delete_report(self):
        """Test that a logged in user can add a report, open it, and delete it."""
        self.login()
        nr_reports = len(self.driver.find_elements_by_class_name("card"))
        self.driver.find_element_by_class_name("button.primary").click()
        cards = self.wait.until(nr_elements((By.CLASS_NAME, "card"), nr_reports + 1))
        new_report = [card for card in cards if "New report" in card.text][-1]
        new_report.click()
        self.assert_text_to_be_present_in_element(self.driver.find_element_by_class_name("header"), "New report")
        self.driver.find_element_by_class_name("caret").click()
        self.driver.find_element_by_class_name("button.negative").click()
        self.wait.until(nr_elements((By.CLASS_NAME, "card"), nr_reports))

    def test_change_overview_title(self):
        """Test that a logged in user can change the overview title."""
        self.login()
        self.driver.find_element_by_class_name("caret").click()
        form = self.driver.find_element_by_tag_name("form")
        form.find_element_by_tag_name("input").send_keys("OVERVIEW")
        self.driver.find_element_by_class_name("caret").click()
        self.assert_text_to_be_present_in_element(self.driver.find_element_by_class_name("header"), "OVERVIEW")
