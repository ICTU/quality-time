Feature: measurement entities
  Managing metric entities: marking them as confirmed, false positive, won't fix, etc.

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric with type "complex_units"

  Scenario: when entities are unchanged a new measurement is not added
    Given an existing source
    When the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    And the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    Then the metric has one measurement

  Scenario: when entities are changed a new measurement is added
    Given an existing source
    When the collector measures "1"
      | key | value | notes |
      | 1   | 1     | foo   |
    And the collector measures "1"
      | key | value | notes |
      | 1   | 1     | bar   |
    Then the metric has two measurements

  Scenario: when an entity key changes, a new measurement is added with the new key and the old status
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"
    When the collector measures "120"
      | key | old_key | story_points |
      | a   | 1       | 100          |
      | b   | 2       | 20           |
    Then the metric status is "target_not_met"

  Scenario: when an entity key disappears, it's marked as orphaned so that when it reappears, its status is still there
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    And the client sets the status of entity 1 to "false_positive"
    And the collector measures "20"
      | key | story_points |
      | 2   | 20           |
    And the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_not_met"

  Scenario: mark an entity as false positive
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_not_met"

  Scenario: an entity marked as false positive disappears on the next measurement
    Given an existing metric with type "user_story_points"
    And an existing source with type "azure_devops"
    When the collector measures "120"
      | key | story_points |
      | 1   | 100          |
      | 2   | 20           |
    Then the metric status is "target_met"
    When the client sets the status of entity 1 to "false_positive"
    Then the metric status is "target_not_met"
    When the collector measures "20"
      | key | story_points |
      | 2   | 20           |
    Then the metric status is "target_not_met"
