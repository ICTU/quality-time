Feature: report
  Creating, editing, and removing reports

  Background: the client is logged in
    Given a logged-in client

  Scenario: add report
    When the client creates a report
    Then the report title is "New report"

  Scenario: delete report
    Given an existing report
    When the client deletes the report
    Then the report does not exist

  Scenario: copy report
    Given an existing report
    When the client copies the report
    Then the report title is "New report (copy)"

  Scenario: copy report with subject
    Given an existing report
    And an existing subject
    When the client copies the report
    Then the report title is "New report (copy)"
    And the report contains 1 subject

  Scenario: change report title
    When the client creates a report
    And the client changes the report title to "New title"
    Then the report title is "New title"

  Scenario: export report as pdf
    When the client creates a report
    And the client downloads the report as pdf
    Then the client receives the pdf

  Scenario: export report as json
    When the client creates a report
    And the client downloads the report as json
    Then the client receives the json

  Scenario: export report as json with own public key
    When the client creates a report
    And the client downloads the report as json with his own public key
    Then the client receives the json

  Scenario: import report
    When the client imports a report
      """
      {
        "title": "Imported report",
        "report_uuid": "imported_report",
        "subjects": [
          {
            "name": "Imported subject",
            "type": "software",
            "metrics": [
              {
                "type": "violations",
                "sources": [
                  {
                    "type": "sonarqube",
                    "parameters": {
                      "url": "https://sonarcloud.io"
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
      """
    Then the report title is "Imported report"

  Scenario: time travel to the past, before the report existed
    When the client creates a report
    And the client enters a report date that's too old
    Then the report does not exist

  Scenario: time travel to the future
    When the client creates a report
    And the client enters a future report date
    Then the report title is "New report"

  Scenario: time travel to the past
    When the client creates a report
    And the client enters a report date that's not too old
    Then the report title is "New report"

  Scenario: get non-existent report
    When the client gets a non-existing report
    Then the report does not exist
