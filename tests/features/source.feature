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

  Scenario: move source to another report
    Given an existing source
    And an existing report
    And an existing subject
    And an existing metric
    When the client moves the source to the metric
    Then the metric contains the source

  Scenario: move source within report
    Given an existing source
    And an existing subject
    And an existing metric
    When the client moves the source to the metric
    Then the metric contains the source

  Scenario: move source within subject
    Given an existing source
    And an existing metric
    When the client moves the source to the metric
    Then the metric contains the source

  Scenario: change source name
    Given an existing source
    When the client changes the source name to "New name"
    Then the source name is "New name"

  Scenario: change source name to the same value
    Given an existing source with name "Source"
    When the client changes the source name to "Source"
    Then the source name is "Source"

  Scenario: change source type
    Given an existing source
    When the client changes the source type to "azure_devops"
    Then the source type is "azure_devops"

  Scenario: change source position
    Given an existing source with name "A"
    And an existing source with name "B"
    When the client changes the source position to "first"
    Then the metric's first source has name "B"
    And the metric's last source has name "A"
