Feature: notification destinations
  Creating, editing, and removing notification destinations

  Background: the client is logged in and a report exists
    Given a logged-in client
    And an existing report

  Scenario: add notification destination
    When the client adds a new notification destination
    Then the notification_destination name is "new"

  Scenario: change notification destination name
    Given a notification destination
    When the client changes the notification_destination name to "New name"
    Then the notification_destination name is "New name"

  Scenario: Delete notification destination
    Given a notification destination
    When the client deletes the notification_destination
    Then the notification_destination does not exist
