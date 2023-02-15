Feature: reports
  Editing the reports overview

  Background: the client is logged in
    Given a logged-in client

  Scenario: edit title
    When the client changes the reports_overview title to "Reports overview"
    Then the reports_overview title is "Reports overview"

  Scenario: add comment without html
    When the client changes the reports_overview comment to "Text"
    Then the reports_overview comment is "Text"

  Scenario: add comment with html
    When the client waits a second
    And the client changes the reports_overview comment to "<b><i>Emphasized text</i></b>"
    Then the reports_overview comment is "<b><i>Emphasized text</i></b>"

  Scenario: add comment with dangerous html
    When the client waits a second
    And the client changes the reports_overview comment to "Cleaned<script>alert('Danger')</script>"
    Then the reports_overview comment is "Cleaned"

  Scenario: get the reports overview measurements
    When the client gets the current reports overview measurements
    Then the server returns the reports overview measurements

  Scenario: get the reports overview measurements with time travel
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client waits a second
    And the client gets past reports overview measurements
    Then the server returns the reports overview measurements
