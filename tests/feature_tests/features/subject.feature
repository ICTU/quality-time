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

  Scenario: copy subject with metric
    Given an existing subject
    And an existing metric
    When the client copies the subject
    Then the subject name is "CI-environment (copy)"
    And the subject contains 1 metric

  Scenario: move subject
    Given an existing subject
    And an existing report
    When the client moves the subject to the report
    Then the report contains the subject

  Scenario: change subject name
    Given an existing subject
    When the client changes the subject name to "New name"
    Then the subject name is "New name"

  Scenario: change subject name to the same value
    Given an existing subject with name "Subject"
    When the client changes the subject name to "Subject"
    Then the subject name is "Subject"

  Scenario: add comment without html
    Given an existing subject
    When the client changes the subject comment to "Text"
    Then the subject comment is "Text"

  Scenario: add comment with html
    Given an existing subject
    When the client changes the subject comment to "<b><i>Emphasized text</i></b>"
    Then the subject comment is "<b><i>Emphasized text</i></b>"

  Scenario: add comment with dangerous html
    Given an existing subject
    When the client changes the subject comment to "Text<script>alert('Danger')</script>"
    Then the subject comment is "Text"

  Scenario: change subject position to first
    Given an existing subject with name "A"
    And an existing subject with name "B"
    And an existing subject with name "C"
    When the client changes the subject position to "first"
    Then the report's first subject has name "C"
    And the report's last subject has name "B"

  Scenario: change subject position to last
    Given an existing subject with name "A"
    And an existing subject with name "B"
    And an existing subject with name "C"
    When the client changes the subject position to "last"
    Then the report's first subject has name "A"
    And the report's last subject has name "C"

  Scenario: get recent measurements of subject
    Given an existing subject
    And an existing metric
    And an existing source
    When the collector measures "0"
    Then the subject has "1" measurements

  Scenario: recent subject has no old measurements
    Given an existing subject
    And an existing metric
    And an existing source
    When the collector measures "0"
    Then the subject had "0" measurements
