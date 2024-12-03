"""Unit tests for the TestNG XML test suites collector."""

from .base import TestNGCollectorTestCase


class TestNGTestSuitesTest(TestNGCollectorTestCase):
    """Unit tests for the TestNG XML test suites collector."""

    METRIC_TYPE = "test_suites"
    TESTNG_XML = """
    <testng-results skipped="2" failed="2" ignored="2" total="8" passed="2">
      <suite name="suite1">
        <test name="test1">
          <class name="class1">
            <test-method status="PASS"></test-method>
            <test-method status="FAIL"></test-method>
            <test-method status="SKIP"></test-method>
            <test-method status="IGNORE"></test-method>
          </class>
        </test>
      </suite>
      <suite name="suite2">
        <test name="test2">
          <class name="class2">
            <test-method status="IGNORE"></test-method>
          </class>
        </test>
      </suite>
      <suite name="suite3">
        <test name="test3">
          <class name="class3">
            <test-method status="FAIL"></test-method>
          </class>
        </test>
      </suite>
      <suite name="suite4">
        <test name="test4">
          <class name="class4">
            <test-method status="SKIP"></test-method>
          </class>
        </test>
      </suite>
      <suite name="suite5">
        <test name="test5">
          <class name="class5">
            <test-method status="PASS"></test-method>
          </class>
        </test>
      </suite>
    </testng-results>
    """

    def setUp(self):
        """Extend to set up TestNG test data."""
        super().setUp()
        self.expected_entities = [
            self.create_entity("suite1", "failed", passed=1, ignored=1, failed=1, skipped=1),
            self.create_entity("suite2", "ignored", ignored=1),
            self.create_entity("suite3", "failed", failed=1),
            self.create_entity("suite4", "skipped", skipped=1),
            self.create_entity("suite5", "passed", passed=1),
        ]

    def create_entity(  # noqa: PLR0913
        self,
        name: str,
        result: str,
        passed: int = 0,
        ignored: int = 0,
        failed: int = 0,
        skipped: int = 0,
    ) -> dict[str, str]:
        """Create a JUnit measurement entity."""
        return {
            "key": name,
            "suite_name": name,
            "suite_result": result,
            "tests": str(passed + ignored + failed + skipped),
            "passed": str(passed),
            "ignored": str(ignored),
            "failed": str(failed),
            "skipped": str(skipped),
        }

    async def test_suites(self):
        """Test that the number of suites is returned."""
        response = await self.collect(get_request_text=self.TESTNG_XML)
        self.assert_measurement(response, value="5", total="5", entities=self.expected_entities)

    async def test_failed_suites(self):
        """Test that the failed suites are returned."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.TESTNG_XML)
        self.assert_measurement(
            response, value="2", total="5", entities=[self.expected_entities[0], self.expected_entities[2]]
        )
