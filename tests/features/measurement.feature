Feature: measurement
  Measuring metrics

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric

  Scenario: the metric has no source
    When the collector gets the metrics to measure
    Then the metric needs to be measured

  Scenario: the metric is measured and meets the target
    Given an existing source
    When the collector measures "0"
    Then the metric status is "target_met"

  Scenario: the metric is measured and doesn't meet the target
    Given an existing source
    When the collector measures "100"
    Then the metric status is "target_not_met"
