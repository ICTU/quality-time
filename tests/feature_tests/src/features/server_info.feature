Feature: server info
  Information about the server can be retrieved

  Scenario: get the server information
    When the client gets the server information
    Then the server information is returned

  Scenario: healthcheck API-server
    Given a healthy server
    When a client checks the server health
    Then the server answers

  Scenario: API-endpoints documentation
    When the client gets the server documentation
    Then the server documentation is returned
