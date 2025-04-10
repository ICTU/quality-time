Feature: authentication
  Log in and log out users. Only authenticated users can edit things.

  Scenario: a user who hasn't logged in can't edit
    Given a logged-in client
    Given a logged-out client
    When the client tries to create a report
    Then the server tells the client to log in

  Scenario: wrong credentials
    When the client tries to log in with incorrect credentials
    Then the server tells the client the credentials are incorrect

  Scenario: non-existing endpoint
    When the client tries to access a non-existing endpoint
    Then the server tells the client the endpoint does not exist

  Scenario: change editors
    When jadoe logs in
    And the client changes the reports_overview permissions to "{"edit_reports": ["jadoe", "other_user"], "edit_entities": []}"
    And the client waits a second
    Then the reports_overview permissions is "{"edit_reports": ["jadoe", "other_user"], "edit_entities": []}"
    When the client logs out
    And jodoe logs in
    And the client changes the reports_overview permissions to "{"edit_report": ["jodoe", "admin"]}"
    Then the server tells the client they are not authorized

  Scenario: change editors without including self
    When jadoe logs in
    And the client changes the reports_overview permissions to "{"edit_reports": ["jodoe"], "edit_entities": []}"
    And the client waits a second
    Then the reports_overview permissions is "{"edit_reports": ["jodoe", "jadoe"], "edit_entities": []}"
    When the client changes the reports_overview permissions to "None"
    Then the reports_overview permissions is "None"

  Scenario: get public key
    When the client requests the public key
    Then the client receives the public key
