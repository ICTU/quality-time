Feature: Technical Debt

  As a quality manager
  I want to manage technical debt
  So that it is clear which metrics need immediate attention and which do not

  Scenario Outline: Accept technical debt
    Given I visit the report and login
    And I make sure the Metric debt target is <debt_target>, Metric target is <metric_target> and Accept technical debt <accept_td>
    And a metric whose measurement value is <start_value> as the target value
    When the quality manager changes debt target to <debt_changed>, Metric target to <metric_changed> and Accept technical debt to <accept_td_changed>
    Then the metric is marked as <end_value>
    Examples:
      | debt_target | metric_target | accept_td | start_value      | end_value        | debt_changed | metric_changed | accept_td_changed |
      | 0           | 0             | 1         | x large icon     | money large icon | 200          | 0              | 2                 |
      | 200         | 0             | 2         | money large icon | check large icon | 0            | 200            | 1                 |
      | 200         | 0             | 2         | money large icon | x large icon     | 0            | 0              | 1                 |
