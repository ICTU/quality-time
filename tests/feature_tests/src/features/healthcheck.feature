Feature: healthcheck

  Scenario: healthcheck external server
    Given a healthy external server
    When a client checks the external server health
    Then the external server answers

  Scenario: healthcheck internal server
    Given a healthy internal server
    When a client checks the internal server health
    Then the internal server answers
