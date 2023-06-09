Feature: metric issues
  Creating, editing, and removing metric issues

  Background: the client is logged in and a report with a subject exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric with issue_ids "123"
    And an existing source
    And the collector has measured "42"

  Scenario: valid issue tracker and metric with issue (also set the same attribute twice to test idempotency)
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_url to "https://jira"
    And the client waits a second
    And the collector measures issue '123' status 'Completed'
    And the client waits a second
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

  Scenario: issue tracker options are missing because there's no (mock) Jira in our feature test setup
    When the client retrieves the issue tracker options
    Then the issue tracker options are missing

  Scenario: issue id suggestions
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    Then the issue id suggestions are missing

  Scenario: creating a new issue without an issue tracker
    When the client opens a new issue
    Then the new issue response error is 'Issue tracker has no URL configured.'

  Scenario: creating a new issue with an incompletely configured issue tracker
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client opens a new issue
    Then the new issue response error is 'Issue tracker has no project key configured.'

  Scenario: creating a new issue with an completely configured issue tracker
    When the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_project_key to "KEY"
    And the client changes the report tracker_issue_type to "Task"
    And the client opens a new issue
    Then the new issue response error is 'Failed to resolve'

  Scenario: completing all issues ignores the accepted technical debt, adding a new issue unignores it
    When the client waits a second
    And the client changes the metric accept_debt to "True"
    And the client waits a second
    And the client changes the metric debt_target to "100"
    And the client waits a second
    Then the metric status is "debt_target_met"
    When the collector measures '42' with issue '123' status 'Completed'
    And the client waits a second
    Then the metric status is "target_met"
    When the client changes the metric issue_ids to "123,124"
    And the client waits a second
    Then the metric status is "debt_target_met"
