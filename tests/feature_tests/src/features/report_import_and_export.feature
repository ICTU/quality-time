Feature: report
  Importing and exporting reports

  Background: the client is logged in
    Given a logged-in client

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

  Scenario: export report as JSON via the internal API
    When the client creates a report
    And the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    And the client changes the report tracker_password to "secret"
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    And the client sets the source parameter url to "https://public"
    And the client sets the source parameter password to "secret"
    And the client downloads the report as JSON via the internal API
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

  Scenario: import report with credentials encrypted for another Quality-time instance
    When the client imports a report
      """
      {
        "report_uuid": "b2555b79-f87d-4a2e-ac3e-86c12e438167",
        "title": "Imported report without credentials",
        "subjects": {
          "8a969312-760e-444a-a1f1-522ac1cf7f83": {
            "type": "software",
            "name": null,
            "metrics": {
              "68a50d8a-d23f-4c1f-ab35-e5786aa87307": {
                "type": "issues",
                "sources": {
                  "02ec35e6-6b80-4348-8fb4-0357336061cc": {
                    "type": "jira",
                    "parameters": {
                      "api_version": "v3",
                      "jql": "textfields ~ \"test\"",
                      "username": "jodoe@example.org",
                      "password": [
                        "c3mxuASvSdv+CC8qYdBSDGLRWgPJ+d8D8YrIqxnbVGYTeMcLEtUPdliN4o34e1dCPGDhhNwQFkZRnql2bc89Ff7rdfbr9WZ7OJS75duE1c6MkCoGs9FH7hIkMhsE6mKQ8QxR3I/ujtfLMGvgr0kCzUh8aQoLbg3CEnDmXZxzCGJmaVVFrXGKckg6P6lQnPrg7wjTKG31oC5TG0YYO3DyfQB7G0wLh3zpE90GYWqhWFlOHUhtHj6Ws+HgO1IUMb50pdVoLCxUzfZXv1rHfwWEKCvKtQx+Z7PsKLO1tGlQhX/TOKmYWI8/QGiZfNA8OZpKEwFVeqlNIovgZfDqTKqoqVmaQ47jodL57DYXlTuMTwxubCdojc71BEv61ar9+VcY1y4JYHPnw3RVV3kM+1iISlP+B9qINdZwqp30Ioa9w1X5bQyasR03wnp8PY0dVwpwbDrQDuHmGWki20Xvte8XfHTSS7BG95T5HwnWFd501NMGIofw9W8vqLpTFPhnAb8fSMKEXOq/VHixDay60zg6t6xzBNfzc8dVvt2YoabyLa7KdRpXWpdvW90UaNX5ZkGiltWkvhlqi8oUcKP3DAry4LuxQG232YcoQVvS1slaf4EBla+czfNkKCBBeVgZfdSrjXlj34cbZVjZylJojSDcOYAduTns/3R2H93b8uJfLgg=",
                        "gAAAAABp2l2uHA2n-VjFUWk-UF0_R4mqmP7c2r9vVv5H5mUuqtZu_pCtfgORN-BWVj41xj5j21CgKrsTFRxC5FBgP5zMOm1dn-uS6oMZ9a5bfT6B3N8wnWVYouQwY9Mw458_sjFrEGrNbMAKR_YEy2NVAyjSl06NQnhpUQjabvqP7Z_UvwEEHgTFbwLUK1Z_xdsSMqthE3Ghsk7Nz4NyLbAiIl2Izt0ywHiZo47aPW1ctHpdkehiDSkBC6menk-72lkwnLNVISDJx8_LXly2-U3mmvTQbcvS_m9k4gaFN-vq-e-xOE5HWW03aQmMkcdoVEewOIyYHdX8fl1aciAnZ7P17yaT70QQJw=="
                      ],
                      "private_token": "",
                      "url": "https://quality-time.atlassian.net"
                    }
                  }
                }
              }
            }
          }
        },
        "issue_tracker": {
          "parameters": {
            "private_token": [
              "f3ZUNSG/mllHCTQ+MMLagPTLSIk2Fckb92EyqktOOD0OyOrOtERpr3ZYgsaLE3xueZfb0KXOclV4jn8XB0TooCh7b/hFAqeScsqyq7asX6hDpF+ZETeg3sSLHyR3lPxu8qTuJVMz3qG9qlP3fEsoPeA7aINmSfd9G7yC1L9pMQdqtedTNY0sbqVSxLSy1eiUYLJilq/lShcZK1EFZ3b5Ew0ZtyTnZNdBV3UBiyPe2iUQwS1iuLA0PWhoHS0mPAjzjCk2dIJCMTIr5MY+mc5k8V+R2gYZaEnR6qnfqbpWXl0NHyxQHOdj66hC2SKD7V03J1UaO+v0VnssCUfLgouX9ISgaDsGk6XicWue8VpUPbsaquTtnmU9d10rTcwDc5Rh/Y4Pw4djXP7MvltqExuHayZ9cPa3y798J20o38Lbbh+yUbwwdzuL4JcwEETeFkvGUmZSMlQoTAgaQXdU9R9ljdSJxAWL0xZoq15C3MGf4WzMoZBKUUfDt/6Sv+Z59eeM8tKtYGetWsYcwdnEzvuchPAqYw2QxoGhodjgcNrRrOy8hMw6vt/jNZR1UegwuADAQUN9kR6D5D50IcGy/RXektCRYzobh1BDp6Iut/8lQRTD9ZBd9LHGQjxgdQ1oSEYlZ37lpuvYp3R1mOqGfn6QBQEsJEXkSF9U2QN3j+wfRZs=",
              "gAAAAABp2l4uqOiWc7Qe6nBIp9Q-JDJVa2ddI3VQ5a7oEUYO9eoCzuS_jgR4Q1p5UvWtOsUN2_EHu0TNACW2054HEq2UCXVPSg=="
            ]
          }
        }
      }
      """
    Then the report title is "Imported report without credentials"

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
