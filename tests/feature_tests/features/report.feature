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
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "test"
    And the client downloads the report as json
    Then the client receives the json

  Scenario: export report as json with own public key
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "['item_1', 'item_2']"
    And the client downloads the report as json with his own public key
    Then the client receives the json

  Scenario: export json report by unauthenticated client
    When the client creates a report
    And the client logs out
    And the client downloads the report as json
    Then the server tells the client to log in

  Scenario: re-import report
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "['item_1', 'item_2']"
    And the client creates a source
    And the client sets the source parameter password to "test_password"
    And the client downloads the report as json
    And the client re-imports a report
    Then the report title is "New report"

  Scenario: import report with unencrypted credentials
    When the client imports a report
      """
      {
        "title": "Imported report",
        "report_uuid": "imported_report",
        "subjects": {
          "subject_uuid": {
            "name": "Imported subject",
            "type": "software",
            "metrics": {
              "metric_uuid": {
                "type": "violations",
                "sources": {
                  "source_uuid": {
                    "type": "sonarqube",
                    "parameters": {
                      "url": "https://sonarcloud.io",
                      "password": "unencrypted password"
                    }
                  }
                }
              }
            }
          }
        }
      }
      """
    Then the report title is "Imported report"

  Scenario: failed import report
    When the client imports a report
      """
      {
        "title": "Failed report",
        "report_uuid": "failed_report",
        "subjects": {
          "subject_uuid": {
            "name": "Imported subject",
            "type": "software",
            "metrics": {
              "metric_uuid": {
                "type": "violations",
                "sources": {
                  "source_uuid": {
                    "type": "sonarqube",
                    "parameters": {
                      "url": "https://sonarcloud.io",
                      "password": ["message", "not_properly_encrypted_password"]
                    }
                  }
                }
              }
            }
          }
        }
      }
      """
    Then the import failed

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
