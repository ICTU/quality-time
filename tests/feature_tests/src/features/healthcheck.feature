Feature: healthcheck

  Scenario: healthcheck API-server
    Given a healthy server
    When a client checks the server health
    Then the server answers
