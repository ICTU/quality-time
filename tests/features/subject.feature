Feature: subject
  Creating, editing, and removing subjects

  Background: the client is logged in and a report exists
    Given a logged-in client
    And a report

  Scenario: add subject
    When the client creates a subject
    Then the subject type is "ci"
