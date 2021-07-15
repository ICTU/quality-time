Feature: reports
  Editing the reports overview

  Background: the client is logged in
    Given a logged-in client

  Scenario: edit title
    When the client changes the reports_overview title to "Reports overview"
    Then the reports_overview title is "Reports overview"
