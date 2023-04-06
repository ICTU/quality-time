Feature: getting the data model

  Scenario: get the data model
    When the client gets the most recent data model
    Then the server returns the most recent data model

  Scenario: get the data model twice
    When the client gets the most recent data model
    And the client gets the most recent data model
    Then the server returns a 304

  Scenario: get an old data model
    When the client gets a data model from too long ago
    Then the server returns an empty data model
