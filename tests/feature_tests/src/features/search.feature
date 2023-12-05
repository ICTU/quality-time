Feature: search
  Searching metrics, reports, sources, or subjects

  Background: the client is logged in and two reports exist
    Given a logged-in client
    And an existing report with title "Search: report 1"

  Scenario: search report
    Given an existing report with title "Search: report 2"
    When the client searches a report with title "Search: report 2"
    Then the search results contain the uuid of the report

  Scenario: no match report
    When the client searches a report with title "This query does not match"
    Then the search results are empty

  Scenario: no domain objects of the requested type
    When the client searches a subject with title "Subject"
    Then the search results are empty

  Scenario: invalid query
    When the client searches a report without query parameters
    Then the search results contain an error message

  Scenario: search source
    Given an existing subject
    And an existing metric
    And an existing source with name "Source 1" and parameter url "https://source1"
    And an existing source with name "Source 2" and parameter url "https://source2"
    When the client searches a source with url "https://source2"
    Then the search results contain the uuid of the source
