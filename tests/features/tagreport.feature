Feature: tag reports
  Tag reports are read-only reports that contain all metrics from all reports with a specific tag

  Background: the client is logged in
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric

  Scenario: tag reports for unused tags are empty
    When the client gets the tag report for the tag "unused_tag"
    Then the tag report is empty

  Scenario: tag reports only contain metrics with the specified tag
    Given an existing metric with tags "tag_report_test"
    When the client gets the tag report for the tag "tag_report_test"
    Then the tag report with tag "tag_report_test" has only metrics with said tag
