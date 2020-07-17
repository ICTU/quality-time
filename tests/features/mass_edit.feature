Feature: mass edit
  Editing multiple source parameters at once

  Background: the client is logged in and a report exists, with a subject that has one metric with a source
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric
    And an existing source

  Scenario: mass edit url of metric sources
    Given an existing source
    When the client changes the source parameter url to "https://new-url" with scope "metric"
    Then the parameter url of the metric's sources is "https://new-url"

  Scenario: mass edit url of subject sources
    Given an existing metric
    And an existing source
    When the client changes the source parameter url to "https://new-url" with scope "subject"
    Then the parameter url of the subject's sources is "https://new-url"

  Scenario: mass edit url of report sources
    Given an existing subject
    And an existing metric
    And an existing source
    When the client changes the source parameter url to "https://new-url" with scope "report"
    Then the parameter url of the report's sources is "https://new-url"

  Scenario: mass edit url of all sources
    Given an existing report
    And an existing subject
    And an existing metric
    And an existing source
    When the client changes the source parameter url to "https://new-url" with scope "reports"
    Then the parameter url of all sources is "https://new-url"
