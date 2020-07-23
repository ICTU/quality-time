Feature: measurement updates
  Measurement updates

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric
    And an existing source

  Scenario: the client connects to the measurement updates
    When the client connects to the number of measurements stream
    Then the server sends the number of measurements init message
    And the server skips the next update because nothing changed

  Scenario: the client connects to the measurement updates
    When the client connects to the number of measurements stream and the collector adds a measurement
    Then the server sends the number of measurements update message
