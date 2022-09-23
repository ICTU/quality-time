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

  Scenario: copy metric with source
    Given an existing metric
    And an existing source
    When the client copies the metric
    Then the metric name is "Accessibility violations (copy)"
    And the metric contains 1 source

  Scenario: move metric to another report
    Given an existing metric
    And an existing report
    And an existing subject
    When the client moves the metric to the subject
    Then the subject contains the metric

  Scenario: move metric within report
    Given an existing metric
    And an existing subject
    When the client moves the metric to the subject
    Then the subject contains the metric

  Scenario: change metric type
    Given an existing metric
    When the client changes the metric type to "violations"
    Then the metric type is "violations"

  Scenario: change metric type of metric with source
    Given an existing metric
    And an existing source
    When the client changes the metric type to "violations"
    Then the metric contains 1 source

  Scenario: change metric type of metric with source and measurement
    Given an existing metric
    And an existing source
    When the collector measures "100"
    Then the metric status is "target_not_met"
    When the client waits a second
    And the client changes the metric type to "violations"
    Then the metric contains 1 source
    And the metric status is "None"

  Scenario: change technical debt target after changing metric type of metric with measurement
    Given an existing metric
    And an existing source
    When the collector measures "100"
    Then the metric status is "target_not_met"
    When the client waits a second
    And the client changes the metric type to "violations"
    Then the metric contains 1 source
    And the metric status is "None"
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: change metric name
    Given an existing metric
    When the client changes the metric name to "New name"
    Then the metric name is "New name"

  Scenario: change metric name to the same value
    Given an existing metric with name "Metric"
    When the client changes the metric name to "Metric"
    Then the metric name is "Metric"

  Scenario: change metric position
    Given an existing metric with name "A"
    And an existing metric with name "B"
    When the client changes the metric position to "first"
    Then the subject's first metric has name "B"
    And the subject's last metric has name "A"

  Scenario: add comment without html
    Given an existing metric
    When the client changes the metric comment to "Text"
    Then the metric comment is "Text"

  Scenario: add comment with html
    Given an existing metric
    When the client changes the metric comment to "<b><i>Emphasized text</i></b>"
    Then the metric comment is "<b><i>Emphasized text</i></b>"

  Scenario: add comment with dangerous html
    Given an existing metric
    When the client changes the metric comment to "Text<script>alert('Danger')</script>"
    Then the metric comment is "Text"
