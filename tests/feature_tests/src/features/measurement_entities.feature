Feature: measurement entities
  Managing metric entities: marking them as confirmed, false positive, won't fix, etc.

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject

  Scenario: when an entity key changes, a new measurement is added with the new key and the old status
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client waits a second
    When the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"

  Scenario: when an entity's source is deleted, the entity status is not kept
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    When the client waits a second
    And the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"
    When the client deletes the source
    When the client waits a second
    And the collector measures "0"
    When the client waits a second
    And the client creates a source with type "azure_devops"
    When the client waits a second
    And the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"

  Scenario: mark an entity as false positive and then unconfirmed
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client waits a second
    And the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"
    When the client waits a second
    And the client sets the status of entity 1 to "unconfirmed"
    Then the metric status is "target_met"

  Scenario: mark an entity as false positive with status end date in the past
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client sets the status of entity 1 to "false_positive"
    And the client waits a second
    And the client sets the status_end_date of entity 1 to "2022-02-02"
    And the client waits a second
    Then the metric status is "target_met"

  Scenario: mark an entity to a different status with the same desired response time
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the client sets the false_positive desired response time to 10
    And the client waits a second
    And the client sets the wont_fix desired response time to 10
    And the client waits a second
    And the client sets the confirmed desired response time to 10
    And the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client sets the status of entity 1 to "false_positive"
    And the client waits a second
    Then the metric status is "target_not_met"
    When the client waits a second
    And the client sets the status of entity 1 to "wont_fix"
    When the client waits a second
    Then the metric status is "target_not_met"
    When the client waits a second
    When the client sets the status of entity 1 to "confirmed"
    And the client waits a second
    Then the metric status is "target_met"
