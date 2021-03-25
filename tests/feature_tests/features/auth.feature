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

  Scenario: change editors
    When jadoe logs in
    And the client changes the reports editors to "jadoe, admin"
    Then the reports editors is "jadoe, admin"
    When the client logs out
    And jodoe logs in
    And the client changes the reports editors to "jodoe, admin"
    Then the server tells the client they are not authorized

  Scenario: change editors without including self
    When jadoe logs in
    And the client changes the reports editors to "jodoe"
    Then the reports editors is "jodoe, jadoe"
    When the client changes the reports editors to "None"
    Then the reports editors is "None"

  Scenario: get public key
    When the client requests the public key
    Then the client receives the public key
