Feature: source
  Creating, editing, and removing sources

  Background: the client is logged in and a report with a subject that has a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric

  Scenario: add source
    When the client creates a source
    Then the source type is "axecsv"

  Scenario: delete source
    Given an existing source
    When the client deletes the source
    Then the source does not exist

  Scenario: copy source
    Given an existing source
    When the client copies the source
    Then the source name is "Axe CSV (copy)"

  Scenario: move source
    Given an existing source
    And an existing report
    And an existing subject
    And an existing metric
    When the client moves the source to the metric
    Then the metric contains the source

  Scenario: change sourcr name
    Given an existing source
    When the client changes the source name to "New name"
    Then the source name is "New name"
