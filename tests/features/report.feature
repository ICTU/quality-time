Feature: report
  Creating, editing, and removing reports

  Background: the client is logged in
    Given a logged-in client

  Scenario: add report
    When the client creates a report
    Then the report title is "New report"

  Scenario: delete report
    Given a report
    When the client deletes the report
    Then the report does not exist

  Scenario: copy report
    Given a report
    When the client copies the report
    Then the report title is "New report (copy)"

  Scenario: change report title
    When the client creates a report
    And the client changes the report title to "New title"
    Then the report title is "New title"
