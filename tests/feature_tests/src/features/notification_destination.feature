Feature: notification destinations
  Creating, editing, and removing notification destinations

  Background: the client is logged in and a report exists
    Given a logged-in client
    And an existing report

  Scenario: add notification destination
    When the client adds a new notification destination
    Then the notification_destination name is "Microsoft Teams webhook"

  Scenario: add notification destination to non-existing report
    When the client adds a notification destination to a non-existing report
    Then the server returns a 404

  Scenario: change notification destination name
    Given a notification destination
    When the client changes the notification_destination name to "New name"
    Then the notification_destination name is "New name"

   Scenario: change notification destination name of non-existing report
    When the client changes a notification_destination name of a non-existing report
    Then the server returns a 404

  Scenario: change notification destination name to the same value
    Given a notification destination
    When the client changes the notification_destination name to "Microsoft Teams webhook"
    Then the notification_destination name is "Microsoft Teams webhook"

  Scenario: delete notification destination
    Given a notification destination
    When the client deletes the notification_destination
    Then the notification_destination does not exist

  Scenario: delete notification destination of non-existing report
    When the client deletes a notification destination of a non-existing report
    Then the server returns a 404

  Scenario: add two notification destinations
    Given a notification destination
    When the client changes the notification_destination name to "New name"
    And the client adds a new notification destination
    Then the notification_destination name is "Microsoft Teams webhook"
