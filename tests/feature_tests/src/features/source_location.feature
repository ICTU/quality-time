Feature: source location
  Creating, editing, and removing source locations

  Background: the client is logged in and a report exists
    Given a logged-in client
    And an existing report

  Scenario: add source location
    When the client creates a source_location
    Then the source_location source_type is "axe_core"

  Scenario: add source location with a source type that has no locations
    When the client attempts to add a source_location with type "calendar"
    Then the last request failed

  Scenario: get source location
    Given an existing source_location
    When the client sets the source location parameter password to "secret"
    And the client gets the source location
    Then the source location response has source_type "axe_core"
    And the source location response has password "this string replaces credentials"

  Scenario: get non-existing source location
    When the client gets a non-existing source location
    Then the last request failed

  Scenario: change source location name
    Given an existing source_location
    When the client changes the source_location location_name to "My source location"
    Then the source_location location_name is "My source location"

  Scenario: change source location name to the same value
    Given an existing source_location
    When the client changes the source_location location_name to "My source location"
    And the client changes the source_location location_name to "My source location"
    Then the source_location location_name is "My source location"

  Scenario: rename source location
    Given an existing source_location
    When the client changes the source_location location_name to "Old name"
    And the client changes the source_location location_name to "New name"
    Then the source_location location_name is "New name"

  Scenario: change source location url
    Given an existing source_location
    When the client sets the source location parameter url to "https://github.com"
    Then the source_location url is "https://github.com"
    And the availability status code equals "200"
    And the availability status reason equals "OK"

  Scenario: change source location url to the same value
    Given an existing source_location
    When the client sets the source location parameter landing_url to "https://github.com"
    And the client sets the source location parameter landing_url to "https://github.com"
    Then the source_location landing_url is "https://github.com"

  Scenario: change source location password
    Given an existing source_location
    When the client sets the source location parameter password to "secret"
    Then the source_location password is "this string replaces credentials"

  Scenario: change source location parameter that is not a location parameter
    Given an existing source_location
    When the client sets the source location parameter jql to "project = QT"
    Then the last request failed

  Scenario: use a source location for a source
    Given an existing subject
    And an existing metric
    And an existing source
    And an existing source_location
    When the client changes the source_location location_name to "My source location"
    And the client sets the source location of the source
    Then the source has the source location

  Scenario: copy a report with a source location
    Given an existing subject
    And an existing metric
    And an existing source
    And an existing source
    And an existing source_location
    When the client sets the source location of the source
    And the client copies the report
    Then the report contains 1 source_location

  Scenario: move a source with a source location to another report
    Given an existing subject
    And an existing metric
    And an existing source
    And an existing source_location
    When the client sets the source location of the source
    Given an existing report
    And an existing subject
    And an existing metric
    When the client moves the source to the metric
    Then the metric contains the source
    And the report contains 1 source_location

  Scenario: delete source location
    Given an existing source_location
    When the client deletes the source_location
    Then the source_location does not exist

  Scenario: delete source location that is in use
    Given an existing subject
    And an existing metric
    And an existing source
    And an existing source
    And an existing source_location
    When the client sets the source location of the source
    And the client deletes the source_location
    Then the last request failed

  Scenario: changes to source locations are logged in the changelog
    Given an existing source_location
    When the client changes the source_location location_name to "My source location"
    Then the source_location changelog reads
      """
      Jane Doe changed the location_name of source location 'Axe-core' in report 'New report' from '' to 'My source location'.
      Jane Doe added a new source location of type 'Axe-core' to report 'New report'.
      """
