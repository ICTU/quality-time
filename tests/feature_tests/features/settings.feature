Feature: settings
  Post and retrieve settings of a logged-in user

  Scenario: a user posts settings
    Given a logged-in client
    When the client posts new settings
      """
      {
        "test_setting": true
      }
      """
    Then the settings have been updated

  Scenario: user settings are retrieved
    Given a logged-in client
    When the client posts new settings
      """
      {
        "test_setting": true
      }
      """
    And the client retrieves settings
    Then the settings are returned
      """
      {
        "test_setting": true
      }
      """