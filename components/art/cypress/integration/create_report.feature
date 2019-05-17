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
    And the quality manager adds a new source
    And the quality manager changes the source type to Random
    Then the metric is marked as <metric_status>
    Examples:
      | metric_target_value | metric_status    |
      | 100                 | frown large icon |
      | 0                   | smile large icon |
