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

  Scenario: add comment without html
   Given an existing report
   When the client changes the report comment to "Text"
   Then the report comment is "Text"

  Scenario: add comment with html
    Given an existing report
    When the client changes the report comment to "<b><i>Emphasized text</i></b>"
    Then the report comment is "<b><i>Emphasized text</i></b>"

  Scenario: add comment with dangerous html
    Given an existing report
    When the client changes the report comment to "Text<script>alert('Danger')</script>"
    Then the report comment is "Text"

  Scenario: export report as pdf
    When the client creates a report
    And the client downloads the report as pdf
    Then the client receives the pdf

  Scenario: export report as json
    When the client creates a report
    And the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_password to "secret"
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter url to "https://public"
    And the client sets the source parameter password to "secret"
    And the client downloads the report as json
    Then the client receives the json

  Scenario: export nonexisting report as json
    When the client downloads the report non_existing_report_uuid as json
    Then the client receives no json

  Scenario: export report as json with own public key
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "['secret_1', 'secret_2']"
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
    And the client sets the source parameter password to "['secret_1', 'secret_2']"
    And the client creates a source
    And the client sets the source parameter password to "secret"
    And the client downloads the report as json
    And the client re-imports a report
    Then the report title is "New report"

  Scenario: import report with unencrypted credentials
    When the client imports a report
      """
      {
        "title": "Imported report",
        "report_uuid": "imported_report",
        "issue_tracker": {
          "parameters": {
            "password": "unencrypted password"
          }
        },
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
                      "password": "unencrypted secret"
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
                      "password": ["message", "not_properly_encrypted_secret"]
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

  Scenario: get non-existent report
    When the client gets a non-existing report
    Then the report does not exist
