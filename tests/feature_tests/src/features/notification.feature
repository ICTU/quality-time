Feature: notification destinations
  Getting the data to send notifications

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And a notification destination
    And an existing subject
    And an existing metric
    And an existing source

  Scenario: get notification data
    When the collector measures "0"
    Then the metric status is "target_met"
    When the client waits a second
    And the collector measures "100"
    Then the metric status is "target_not_met"
    When the notifier gets the notification data
    Then the internal server returns two measurements for the metric
