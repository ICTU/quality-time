"""Unit tests for the JUnit XML tests collector."""

from .base import TestNGCollectorTestCase


class TestNGTestsTest(TestNGCollectorTestCase):
    """Unit tests for the TestNG XML tests collector."""

    METRIC_TYPE = "tests"
    TESTNG_XML = """
    <testng-results skipped="0" failed="1" ignored="1" total="3" passed="1">
      <suite name="suite1" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z">
        <test name="test1" started-at="2020-09-06T19:02:59Z" finished-at="2020-09-06T19:45:45Z">
          <class name="class1">
            <test-method status="PASS" name="method1" is-config="true" started-at="2020-09-06T19:28:40Z" 
              finished-at="2020-09-06T19:28:40Z">
            </test-method>
            <test-method status="PASS" name="method2" started-at="2020-09-06T19:28:40Z" 
              finished-at="2020-09-06T19:29:04Z">
            </test-method> 
            <test-method status="FAIL" name="method3" started-at="2020-09-06T19:28:40Z" 
              finished-at="2020-09-06T19:29:04Z">
            </test-method> 
          </class>
        </test>
      </suite>
    </testng-results>
    """
    EXPECTED_ENTITIES = [
        dict(key="class1_method1", class_name="class1", name="method1", test_result="passed"),
        dict(key="class1_method2", class_name="class1", name="method2", test_result="passed"),
        dict(key="class1_method3", class_name="class1", name="method3", test_result="failed"),
    ]

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(get_request_text=self.TESTNG_XML)
        self.assert_measurement(response, value="3", total="3", entities=self.EXPECTED_ENTITIES)

    async def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.TESTNG_XML)
        self.assert_measurement(response, value="1", total="3", entities=self.EXPECTED_ENTITIES[-1:])

    async def test_zipped_testng_report(self):
        """Test that the number of tests is returned from a zip with TestNG reports."""
        self.set_source_parameter("url", "testng.zip")
        response = await self.collect(get_request_content=self.zipped_report(("testng.xml", self.TESTNG_XML)))
        self.assert_measurement(response, value="3", total="3", entities=self.EXPECTED_ENTITIES)
