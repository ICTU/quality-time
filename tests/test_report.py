import unittest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')


class OpenReportTest(unittest.TestCase):
    """Open a report."""
    def setUp(self):
        self.driver = webdriver.Chrome(options=chrome_options)

    def tearDown(self):
        self.driver.close()

    def test_title(self):
        self.driver.get("http://localhost:5000")
        self.assertTrue(EC.title_contains("Quality-time"))
