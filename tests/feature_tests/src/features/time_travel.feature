Feature: time travel
  Displaying old reports

  Background: the client is logged in
    Given a logged-in client

  Scenario: time travel to the past, before the report existed
    When the client creates a report
    And the client enters a report date that's too old
    Then the report does not exist

  Scenario: time travel to the future
    When the client creates a report
    And the client enters a future report date
    Then the report title is "New report"

  Scenario: time travel to the past and back to the present
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the collector measures "0"
    Then the metric latest_measurement.count.value is "0"
    When the client enters a report date that's not too old
    And the collector measures "100"
    Then the metric latest_measurement.count.value is "0"
    When the client resets the report date
    Then the metric latest_measurement.count.value is "100"

  Scenario: time travel to a time in the past after a report was deleted
    When the client creates a report
    And the client deletes the report
    And the client enters a report date that's not too old
    Then the report does not exist
