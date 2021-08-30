Feature: server info
  Information about the server can be retrieved

  Scenario: get the server information
    When the client gets the server information
    Then the server information is returned

  Scenario: get the internal-server docs
    When the client gets the internal-server information
    Then the internal-server information is returned