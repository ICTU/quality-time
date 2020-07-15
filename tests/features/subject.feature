Feature: subject
  Creating, editing, and removing subjects

  Background: the client is logged in and a report exists
    Given a logged-in client
    And an existing report

  Scenario: add subject
    When the client creates a subject
    Then the subject type is "ci"

  Scenario: delete subject
    Given an existing subject
    When the client deletes the subject
    Then the subject does not exist

  Scenario: copy subject
    Given an existing subject
    When the client copies the subject
    Then the subject name is "CI-environment (copy)"

  Scenario: move subject
    Given an existing subject
    And an existing report
    When the client moves the subject to the report
    Then the report contains the subject

  Scenario: change subject name
    Given an existing subject
    When the client changes the subject name to "New name"
    Then the subject name is "New name"
