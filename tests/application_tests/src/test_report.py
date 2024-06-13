"""Report tests."""

import pathlib
import unittest

from axe_selenium_python import Axe
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.ui import WebDriverWait


class ElementHasNoCCSClass:
    """An expectation for checking that an element has no CSS class.

    locator - used to find the element
    returns the WebElement once it has no particular CSS class
    """

    def __init__(self, locator) -> None:
        self.locator = locator

    def __call__(self, driver):
        """Return the element if it no longer has a CSS class, otherwise False."""
        element = driver.find_element(*self.locator)
        return element if len(element.get_attribute("class")) == 0 else False


class NrElements:
    """An expectation for the number of matching elements."""

    def __init__(self, locator, expected_nr: int) -> None:
        self.locator = locator
        self.expected_nr = expected_nr

    def __call__(self, driver):
        """Return the element if it has the expected number of elements, otherwise False."""
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
        self.driver.get("http://www:8080?hide_toasts=true")  # Hide toasts so they don't block other visual elements

    def tearDown(self):
        """Override to close the driver."""
        self.driver.quit()

    def login(self):
        """Login a user."""
        self.driver.find_element(By.XPATH, '//button[text()="Login"]').click()
        login_form = self.driver.find_element(By.CLASS_NAME, "modal")
        login_form.find_element(By.NAME, "username").send_keys("jadoe")
        login_form.find_element(By.NAME, "password").send_keys("secret")
        login_form.find_element(By.CLASS_NAME, "button").click()
        self.wait.until(ElementHasNoCCSClass((By.TAG_NAME, "body")))  # Wait for body dimmer to disappear

    def test_title(self):
        """Test the title."""
        self.assertTrue(expect.title_contains("Quality-time"))

    def test_open_report(self):
        """Test that the first report can be opened."""
        # The first report is the third card because the first and second card are the legend and export-data cards:
        report = self.driver.find_elements(By.CLASS_NAME, "card")[2]
        report_title = report.find_element(By.CLASS_NAME, "header")
        report.click()
        self.assertTrue(
            expect.text_to_be_present_in_element(self.driver.find_element(By.CLASS_NAME, "header"), report_title)
        )

    def test_login_and_logout(self):
        """Test that a user can login and logout."""
        self.login()
        logout_dropdown = self.driver.find_elements(By.CLASS_NAME, "dropdown")[1]
        logout_dropdown.click()
        logout_menu_item = self.driver.find_element(By.CLASS_NAME, "selected.item")
        logout_menu_item.click()
        self.assertTrue(self.driver.find_element(By.XPATH, '//button[text()="Login"]'))

    def test_add_report(self):
        """Test that a logged-in user can add a report."""
        self.login()
        nr_reports = len(self.driver.find_elements(By.CLASS_NAME, "card"))
        self.driver.find_element(By.CLASS_NAME, "button.primary").click()
        self.wait.until(NrElements((By.CLASS_NAME, "card"), nr_reports + 1))

    def test_report_axe_accessibility(self):
        """Run axe accessibility check on a report."""
        axe = Axe(self.driver)
        axe.inject()

        # Analyze report page
        report = self.driver.find_elements(By.CLASS_NAME, "card")[2]
        report.click()
        results1 = axe.run()

        # Process axe results
        violation_results = results1["violations"]
        axe.write_results(results1, "../../build/a11y.json")
        readable_report = axe.report(violation_results)
        filename = pathlib.Path("../../build/a11y_violations.txt")
        try:
            with filename.open("w", encoding="utf8") as report_file:
                report_file.write(readable_report)
        except OSError:
            self.fail("Could not write axe violations report")

        # If there are moe violations than expected, output the readable report data
        # Fixing the axe violations is on the backlog: https://github.com/ICTU/quality-time/issues/6354
        current_number_of_axe_violations = 6
        self.assertLessEqual(len(violation_results), current_number_of_axe_violations, readable_report)
