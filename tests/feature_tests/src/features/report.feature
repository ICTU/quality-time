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

  Scenario: delete not-existing report
    When the client deletes a non-existing report
    Then the server returns a 404

  Scenario: copy report
    Given an existing report
    When the client copies the report
    Then the reports overview contains 2 reports

  Scenario: copy non-existing report
    When the client copies a non-existing report
    Then the server returns a 404

  Scenario: copy report with subject
    Given an existing report
    And an existing subject
    When the client copies the report
    Then the report contains 1 subject

  Scenario: change report title
    When the client creates a report
    And the client changes the report title to "New title"
    Then the report title is "New title"

  Scenario: change report title of non-existing report
    When the client changes a non-existing report title to "New title"
    Then the server returns a 404

  Scenario: add comment without HTML
   Given an existing report
   When the client changes the report comment to "Text"
   Then the report comment is "Text"

  Scenario: add comment with HTML
    Given an existing report
    When the client changes the report comment to "<b><i>Emphasized text</i></b>"
    Then the report comment is "<b><i>Emphasized text</i></b>"

  Scenario: add comment with dangerous HTML
    Given an existing report
    When the client changes the report comment to "Text<script>alert('Danger')</script>"
    Then the report comment is "Text"

  Scenario: add comment with URL
    Given an existing report
    When the client changes the report comment to "https://example-url.org"
    Then the report comment is "<a href="https://example-url.org" target="_blank">https://example-url.org</a>"

  Scenario: add comment with link that has a target
    Given an existing report
    When the client changes the report comment to "<a href='https://example-url.org' target='_top'>https://example-url.org</a>"
    Then the report comment is "<a href="https://example-url.org" target="_top">https://example-url.org</a>"

  Scenario: get report metric status summary
    Given an existing report
    When the client gets the metric status summary
    Then the report metric status summary is returned

  Scenario: remove a tag from all metrics in a report
    Given an existing report with title "Scenario: remove tag"
    And an existing subject
    And an existing metric with tags "security, maintainability"
    When the client removes the tag "security" from the report
    Then the metric tags is "maintainability"

  Scenario: remove a non-existing tag from all metrics in a report
    Given an existing report with title "Scenario: remove non-existing tag"
    And an existing subject
    And an existing metric with tags "maintainability"
    When the client removes the tag "security" from the report
    Then the metric tags is "maintainability"

  Scenario: rename a tag for all metrics in a report
    Given an existing report with title "Scenario: rename tag"
    And an existing subject
    And an existing metric with tags "security, maintainability"
    When the client renames the tag "security" to "safety"
    Then the metric tags is "maintainability, safety"

  Scenario: rename a tag for all metrics in a report to an existing tag
    Given an existing report with title "Scenario: rename tag to existing"
    And an existing subject
    And an existing metric with tags "security, maintainability"
    When the client renames the tag "security" to "maintainability"
    Then the metric tags is "maintainability"

  Scenario: rename a non-existing tag for all metrics in a report
    Given an existing report with title "Scenario: rename non-existing tag"
    And an existing subject
    And an existing metric with tags "maintainability"
    When the client renames the tag "security" to "safety"
    Then the metric tags is "maintainability"

  Scenario: export report as PDF
    When the client creates a report
    And the client downloads the report as PDF
    Then the client receives the PDF

  Scenario: export report as JSON
    When the client creates a report
    And the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_password to "secret"
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter url to "https://public"
    And the client sets the source parameter password to "secret"
    And the client downloads the report as JSON
    Then the client receives the JSON

  Scenario: export nonexisting report as JSON
    When the client downloads the report non_existing_report_uuid as json
    Then the client receives no JSON

  Scenario: export report as JSON with own public key
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "['secret_1', 'secret_2']"
    And the client downloads the report as JSON with his own public key
    Then the client receives the JSON

  Scenario: export JSON report by unauthenticated client
    When the client creates a report
    And the client logs out
    And the client downloads the report as JSON
    Then the server tells the client to log in

  Scenario: re-import report
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter password to "['secret_1', 'secret_2']"
    And the client creates a source
    And the client sets the source parameter password to "secret"
    And the client downloads the report as JSON
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
