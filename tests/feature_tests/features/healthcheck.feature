Feature: healthcheck

  Scenario: server healthcheck
    Given a healthy server
    When a client checks the server health
    Then the server answers

  Scenario: internal-server healthcheck 
    Given a healthy internal-server
    When a client checks the internal-server health
    Then the internal-server answers
