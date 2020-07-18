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
