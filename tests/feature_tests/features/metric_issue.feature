Feature: metric issues
  Creating, editing, and removing metric issues

  Background: the client is logged in and a report with a subject exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric with issue_ids "123"
    And an existing source

  Scenario: valid issue tracker and metric with issue (also set the same attribute twice to test idempotency)
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_url to "https://jira"
    And the collector gets the metrics to measure
    And the collector measures issue '123' status 'Completed'
    Then the issue status name is 'Completed'
    And the issue status connection_error is 'None'
    And the issue status parse_error is 'None'

  Scenario: invalid issue tracker type
    When the client changes the report tracker_type to "this-source-is-no-issue-tracker"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_username to "jadoe"
    And the client changes the report tracker_password to "secret"
    Then the issue status name is 'None'
    And the issue status landing_url is 'None'
    And the issue status connection_error is 'None'
    And the issue status parse_error is 'None'

  Scenario: issue id suggestions
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    Then the issue id suggestions are missing
