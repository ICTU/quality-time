Feature: reports
  Editing the reports overview

  Background: the client is logged in
    Given a logged-in client

  Scenario: edit title
    When the client changes the reports title to "Reports overview"
    Then the reports title is "Reports overview"
