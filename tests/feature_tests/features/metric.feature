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

  Scenario: valid issue tracker and metric with issue (also set the same attribute twice to test idempotency)
    Given an existing metric
    And an existing source
    When the client changes the metric issue_ids to "123"
    And the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_url to "https://jira"
    And the collector gets the metrics to measure
    And the collector measures issue '123' status 'Completed'
    Then the issue status name is 'Completed'
    And the issue status connection_error is 'None' 
    And the issue status parse_error is 'None' 

  Scenario: invalid issue tracker type
    Given an existing metric
    And an existing source
    When the client changes the metric issue_ids to "123"
    And the client changes the report tracker_type to "this-source-is-no-issue-tracker"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_username to "jadoe"
    And the client changes the report tracker_password to "secret"
    Then the issue status name is 'None'
    And the issue status description is 'None'
    And the issue status landing_url is 'None'
    And the issue status connection_error is 'None' 
    And the issue status parse_error is 'None' 
