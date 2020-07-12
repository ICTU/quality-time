Feature: report

  Scenario: add report
    Given a logged-in client
    When the client creates a new report
    Then the server returns OK
    
  Scenario: delete report
    Given a logged-in client
    When the client creates a new report
    And the client deletes the new report
    Then the server returns OK
