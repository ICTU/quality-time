Feature: metric
  Creating, editing, and removing metrics

  Background: the client is logged in and a report with a subject exists
    Given a logged-in client
    And an existing report
    And an existing subject

  Scenario: add metric
    When the client creates a metric
    Then the metric type is "violations"

  Scenario: add metric that is not evaluated by default
    When the client creates a metric with type "software_version"
    And the client creates a source with type "sonarqube"
    And the collector measures "1.1" with status "informative"
    And the client waits a second
    Then the metric status is "informative"

  Scenario: delete metric
    Given an existing metric
    When the client deletes the metric
    Then the metric does not exist

  Scenario: copy metric
    Given an existing metric
    When the client copies the metric
    Then the subject contains 2 metrics

  Scenario: copy metric with source
    Given an existing metric
    And an existing source
    When the client copies the metric
    Then the metric contains 1 source

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
    When the client changes the metric type to "security_warnings"
    Then the metric type is "security_warnings"

  Scenario: change metric type of metric with source
    Given an existing metric
    And an existing source
    When the client changes the metric type to "security_warnings"
    Then the metric contains 1 source

  Scenario: change metric type of metric with source and measurement
    Given an existing metric
    And an existing source
    When the collector measures "100"
    And the client waits a second
    And the client changes the metric type to "security_warnings"
    Then the metric contains 1 source
    And the metric status is "None"

  Scenario: change technical debt target after changing metric type of metric with measurement
    Given an existing metric
    And an existing source
    When the collector measures "100"
    And the client waits a second
    And the client changes the metric type to "security_warnings"
    Then the metric contains 1 source
    And the metric status is "None"
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: accept technical debt, including changing debt attributes
    Given an existing metric
    And an existing source
    When the client accepts the technical debt
    Then the metric status is "debt_target_met"
    When the client does not accept the technical debt
    Then the metric status is "None"
    When the collector measures "100"
    And the client waits a second
    And the client accepts the technical debt
    Then the metric status is "debt_target_met"
    And the metric debt_target is "100"
    When the client waits a second
    And the client does not accept the technical debt
    Then the metric status is "target_not_met"
    And the metric debt_target is "None"
    When the client changes the metric debt_target to "100"
    Then the metric debt_target is "100"
    When the client does not accept the technical debt
    Then the metric status is "target_not_met"
    And the metric debt_target is "None"
    When the client does not accept the technical debt
    Then the metric status is "target_not_met"
    And the metric debt_target is "None"

  Scenario: accept technical debt without desired technical debt response time
    Given an existing metric
    And an existing source
    When the client sets the debt_target_met desired response time to empty
    And the client accepts the technical debt
    Then the metric technical debt end date is empty
    When the client does not accept the technical debt
    And the client sets the debt_target_met desired response time to 10
    And the client accepts the technical debt
    Then the metric technical debt end date is not empty

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

  Scenario: change metric index
    Given an existing metric with name "A"
    And an existing metric with name "B"
    When the client changes the metric position_index to "0"
    Then the subject has a metric at index 0 with name "B"
    And the subject has a metric at index 1 with name "A"

  Scenario: move metric to its current index (no-op)
    Given an existing metric with name "A"
    And an existing metric with name "B"
    When the client changes the metric position_index to "1"
    Then the subject has a metric at index 0 with name "A"
    And the subject has a metric at index 1 with name "B"

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
