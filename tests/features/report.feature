Feature: report

  Scenario: add report
    Given a logged-in client
    When the client creates a new report
    Then the server returns OK
