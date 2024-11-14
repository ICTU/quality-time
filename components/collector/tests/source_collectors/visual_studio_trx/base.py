"""Base classes for Visual Studio TRX test report collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class VisualStudioTRXCollectorTestCase(SourceCollectorTestCase):
    """Base class for Visual Studio TRX collector unit tests."""

    SOURCE_TYPE = "visual_studio_trx"
    VISUAL_STUDIO_TRX_XML = r"""<?xml version="1.0" encoding="utf-8"?>
    <TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
        <Times creation="2024-09-12T11:33:30.3272909+02:00" />
        <Results>
            <UnitTestResult
                executionId="268fd488-12c7-4107-80d8-5df1200cd637"
                testId="63eb0c90-d1fc-a21e-6fc0-3974b0cc65db"
                testName="BestaandeZaakOpenen2"
                computerName="XYZ-BLA-24"
                duration="00:00:01.4635437"
                startTime="2024-09-12T11:33:29.3938415+02:00"
                endTime="2024-09-12T11:33:30.8644329+02:00"
                testType="13cdc9d9-ddb5-4fa4-a97d-d965ccfc6d4b"
                outcome="Failed"
                testListId="8c84fa94-04c1-424b-9868-57a2d4851a1d"
                relativeResultsDirectory="268fd488-12c7-4107-80d8-5df1200cd637"
            />
            <UnitTestResult
                executionId="daf369f6-7c54-482d-a12c-68357679bd78"
                testId="446a0829-8d87-1082-ab45-b2ab9f846325"
                testName="BestaandeZaakOpenen"
                computerName="XYZ-BLA-24"
                duration="00:00:01.7342127"
                startTime="2024-09-12T11:33:27.3275629+02:00"
                endTime="2024-09-12T11:33:29.3909874+02:00"
                testType="13cdc9d9-ddb5-4fa4-a97d-d965ccfc6d4b"
                outcome="Passed"
                testListId="8c84fa94-04c1-424b-9868-57a2d4851a1d"
                relativeResultsDirectory="daf369f6-7c54-482d-a12c-68357679bd78"
            />
        </Results>
        <TestDefinitions>
            <UnitTest name="BestaandeZaakOpenen" id="446a0829-8d87-1082-ab45-b2ab9f846325">
                <TestCategory>
                    <TestCategoryItem TestCategory="FeatureTag" />
                    <TestCategoryItem TestCategory="ScenarioTag1" />
                    <TestCategoryItem TestCategory="JIRA-224" />
                </TestCategory>
                <Execution id="daf369f6-7c54-482d-a12c-68357679bd78" />
                <TestMethod
                    codeBase="C:\XYZ\FrontendTests.dll"
                    adapterTypeName="executor://mstestadapter/v2"
                    className="ClassName"
                    name="BestaandeZaakOpenen"
                />
            </UnitTest>
            <UnitTest name="BestaandeZaakOpenen2" id="63eb0c90-d1fc-a21e-6fc0-3974b0cc65db">
                <TestCategory>
                    <TestCategoryItem TestCategory="FeatureTag" />
                    <TestCategoryItem TestCategory="ScenarioTag2" />
                </TestCategory>
                <Execution id="268fd488-12c7-4107-80d8-5df1200cd637" />
                <TestMethod
                    codeBase="C:\XYZ\FrontendTests.dll"
                    adapterTypeName="executor://mstestadapter/v2"
                    className="ClassName"
                    name="BestaandeZaakOpenen2"
                />
            </UnitTest>
        </TestDefinitions>
    </TestRun>"""
