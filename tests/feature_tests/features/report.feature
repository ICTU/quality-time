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

  Scenario: import report
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
                      "password": [
                        "zhqA7B71yTu1/u59RnbQhXczdEWFKpdSn04mVVixqnYlG6T7426fwAf8LNj9fiwrSG7Qk7LPg8/gQ3/3lQiH159jDdj+VAn89k2sbMKRC5tlSALmoaNL3PHYhoICenlOM+tWXxiZngz8CFaxAV2T1Wi/X0aKFPhcYY9YWoj0xEUjdlIVufwXvZpK2qt29uy0OtqLIFqCQoH+7dU0C4coE8rALttkM/dxhOUUZWybI83VQjA/j+mqzwwGNpD1APLqTRsIi1QL3LL4x9m60qmaJqmUCtSO8QrDk/vLOH0ImCDDP+I0Ggx+B0QRFWFzPxKbHJ0bvTb0hwtI74wosgpHVHWe7SWk741H0xQ2UzG0TWrvnlYJr3porEI5rsIu8HwTVquYJLz7an3215fSeo34J9pmGqneKqXowomW4/ehhtS2ktylNQoLBKEoGw9aglSLcWo14lIrmW+eEhc9qJP7b+9psgho7BwCVprYDZnuvEdZg308wGhHjj2HRLYn9CphltMLOUDoXQhnMtDeOHXdnYauEMu3ZAndIYtO06A6OVh8Sr4jHL/E+jme8sky7RR9s+Mk5gkxfIb6yxc8oYlT2fUGx2LmL7noIiCsJo6NNyHQJYTFlWLAJ8VmkjbdJRwJnBYk1AgMJyQ5QUlIMVwbMg8kPBWWSci26ODeijXh8ow=",
                        "gAAAAABgShzE8ZlHKCKNnuGue5R7G8zPkhYp68hZRz68WAyFK4Sbj1goRdP_g8az_tGC81rlTphlKeDMBZXTenhHk4_it3VEVEi8GBB12yM3SQFVB_pvGbR8WJL_styBi8rI4YzyDu6sHe99cvnveQCM1QEbiL-c_g=="]
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
