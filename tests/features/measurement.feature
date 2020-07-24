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

  Scenario: the metric is measured but an error happens
    Given an existing source
    When the collector encounters a parse error
    Then the metric status is "None"

  Scenario: the metric is not measured and this is accepted as technical debt (e.g. because there's no source yet)
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: the metric is measured, doesn't meet the target, and it's accepted as technical debt
    Given an existing source
    When the collector measures "100"
    And the client changes the metric accept_debt to "True"
    And the client changes the metric debt_target to "100"
    Then the metric status is "debt_target_met"

  Scenario: a measurement that's unchanged is updated
    Given an existing source
    When the collector measures "0"
    And the collector measures "0"
    Then the metric has one measurement

  Scenario: when entities are unchanged a new measurement is not added
    Given an existing source
    When the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    And the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    Then the metric has one measurement

  Scenario: when entities are changed a new measurement is added
    Given an existing source
    When the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    And the collector measures "1"
      | key | value | notes |
      | 1   | 1     | bar   |
    Then the metric has two measurements

  Scenario: mark an entity as false positive
    Given an existing source
    When the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    Then the metric status is "near_target_met"
    When the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_met"
