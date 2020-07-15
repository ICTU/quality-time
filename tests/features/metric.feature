Feature: metric
  Creating, editing, and removing metrics

  Background: the client is logged in and a report with a subject exists
    Given a logged-in client
    And an existing report
    And an existing subject

  Scenario: add metric
    When the client creates a metric
    Then the metric type is "accessibility"

  Scenario: delete metric
    Given an existing metric
    When the client deletes the metric
    Then the metric does not exist

  Scenario: copy metric
    Given an existing metric
    When the client copies the metric
    Then the metric name is "Accessibility violations (copy)"

  Scenario: move metric
    Given an existing metric
    And an existing report
    And an existing subject
    When the client moves the metric to the subject
    Then the subject contains the metric

  Scenario: change metric name
    Given an existing metric
    When the client changes the metric name to "New name"
    Then the metric name is "New name"
