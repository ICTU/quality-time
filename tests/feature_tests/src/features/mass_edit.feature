Feature: mass edit
  Editing multiple source parameters at once

  Background: the client is logged in and a report exists, with a subject that has one metric with a source
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric
    And an existing source with url "https://old-url"

  Scenario: mass edit url of report sources
    Given an existing subject
    And an existing metric
    And an existing source with url "https://old-url"
    When the client sets the source parameter url to "https://new-url" with scope "report"
    Then the parameter url of the report's sources equals "https://new-url"
