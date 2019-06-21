Feature: Create quality report

  As quality manager for a new project
  I want to create a new report
  So that I can monitor the quality of the project

  Scenario Outline: Create report
    Given the quality manager logs in
    When the quality manager creates a new report
    And the quality manager adds a new subject
    And the quality manager adds a new metric
    And the quality manager sets the metric target value to <metric_target_value>
    Then the metric target is <expected_metric_target_value>
    Examples:
      | metric_target_value | expected_metric_target_value |
      | 100                 | 100                          |
      | -1                  | 0                            |
