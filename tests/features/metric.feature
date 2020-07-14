Feature: metric
  Creating, editing, and removing metrics

  Background: the client is logged in and a report with a subject exists
    Given a logged-in client
    And a report
    And a subject

  Scenario: add metric
    When the client creates a metric
    Then the metric type is "accessibility"

  Scenario: delete metric
    Given a metric
    When the client deletes the metric
    Then the metric does not exist

  Scenario: copy metric
    Given a metric
    When the client copies the metric
    Then the metric name is "Accessibility violations (copy)"

  Scenario: move metric
    Given a metric
    And a report
    And a subject
    When the client moves the metric to the subject
    Then the subject contains the metric

  Scenario: change metric name
    Given a metric
    When the client changes the metric name to "New name"
    Then the metric name is "New name"
