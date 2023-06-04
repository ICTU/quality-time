Feature: healthcheck

  Scenario: healthcheck external server
    Given a healthy external server
    When a client checks the external server health
    Then the external server answers
