"""Unit tests for the OJAudit violations collector."""

from ...source_collector_test_case import SourceCollectorTestCase


class OJAuditViolationsTest(SourceCollectorTestCase):
    """Unit tests for the OJAudit violations collector."""

    def setUp(self):
        self.metric = dict(
            type="violations",
            addition="sum",
            sources=dict(source_id=dict(type="ojaudit", parameters=dict(url="https://ojaudit.xml"))),
        )

    async def test_violations(self):
        """Test that the number of violations is returned."""
        ojaudit_xml = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <exception-count>1</exception-count>
  <error-count>0</error-count>
  <warning-count>1</warning-count>
  <incomplete-count>0</incomplete-count>
  <advisory-count>0</advisory-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <children>
      <construct>
        <children>
          <violation>
            <message>a</message>
            <location model="a">
              <line-number>20</line-number>
              <column-offset>4</column-offset>
            </location>
            <values>
              <value>warning</value>
            </values>
          </violation>
        </children>
      </construct>
      <violation>
        <message>b</message>
        <location model="b">
          <line-number>10</line-number>
              <column-offset>2</column-offset>
        </location>
        <values>
          <value>exception</value>
        </values>
      </violation>
    </children>
  </construct>
</audit>"""
        response = await self.collect(self.metric, get_request_text=ojaudit_xml)
        expected_entities = [
            dict(
                component="a:20:4",
                key="894756a0231a17f66b33d0ac18570daa193beea3",
                message="a",
                severity="warning",
                count="1",
            ),
            dict(
                component="b:10:2",
                key="2bdb532d49f0bf2252e85dc2d41e034c8c3e1af3",
                message="b",
                severity="exception",
                count="1",
            ),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_missing_location(self):
        """Test that an exception is raised if the violation location is missing."""
        ojaudit_xml = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <violation>
    <message>a</message>
    <values>
        <value>medium</value>
    </values>
    </violation>
  </construct>
</audit>"""
        response = await self.collect(self.metric, get_request_text=ojaudit_xml)
        self.assertTrue("has no location element" in response["sources"][0]["parse_error"])

    async def test_filter_violations(self):
        """Test that violations of types the user doesn't want to see are not included."""
        ojaudit_xml = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>1</violation-count>
  <exception-count>1</exception-count>
  <error-count>0</error-count>
  <warning-count>0</warning-count>
  <incomplete-count>0</incomplete-count>
  <advisory-count>0</advisory-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
  </models>
  <construct>
    <violation>
      <message>a</message>
      <location model="a">
        <line-number>20</line-number>
        <column-offset>4</column-offset>
      </location>
      <values>
          <value>exception</value>
      </values>
    </violation>
  </construct>
</audit>"""
        self.metric["sources"]["source_id"]["parameters"]["severities"] = ["error"]
        response = await self.collect(self.metric, get_request_text=ojaudit_xml)
        self.assert_measurement(response, value="0", entities=[])

    async def test_ignore_duplicated_violations(self):
        """Test that violations with the same model, message, location, etc. are ignored."""
        ojaudit_xml = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <exception-count>1</exception-count>
  <error-count>0</error-count>
  <warning-count>1</warning-count>
  <incomplete-count>0</incomplete-count>
  <advisory-count>0</advisory-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
  </models>
  <construct>
    <children>
      <construct>
        <children>
          <violation>
            <message>a</message>
            <location model="a">
              <line-number>20</line-number>
              <column-offset>4</column-offset>
            </location>
            <values>
              <value>warning</value>
            </values>
          </violation>
          <violation>
            <message>a</message>
            <location model="a">
              <line-number>20</line-number>
              <column-offset>4</column-offset>
            </location>
            <values>
              <value>warning</value>
            </values>
          </violation>
        </children>
      </construct>
    </children>
  </construct>
</audit>"""
        response = await self.collect(self.metric, get_request_text=ojaudit_xml)
        expected_entities = [
            dict(
                component="a:20:4",
                key="894756a0231a17f66b33d0ac18570daa193beea3",
                message="a",
                severity="warning",
                count="2",
            )
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)
