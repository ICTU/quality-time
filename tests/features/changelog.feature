Feature: changelog
  Get a changelog with recent changes

  Background:
    Given a logged-in client
    When the client changes the reports title to "Reports"
    When the client changes the reports title to "Reports overview"

  Scenario: create a report
    When the client creates a report
    Then the changelog reads
      """
      admin created a new report.
      admin changed the title of the reports overview from 'Reports' to 'Reports overview'.
      """
    And the report changelog reads
      """
      admin created a new report.
      """

  Scenario: create a report and a subject
    When the client creates a report
    And the client creates a subject
    Then the changelog reads
      """
      admin created a new subject in report 'New report'.
      admin created a new report.
      admin changed the title of the reports overview from 'Reports' to 'Reports overview'.
      """
    And the report changelog reads
      """
      admin created a new subject in report 'New report'.
      admin created a new report.
      """
    And the subject changelog reads
      """
      admin created a new subject in report 'New report'.
      """

  Scenario: create a report, a subject, and a metric
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    Then the changelog reads
      """
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      admin created a new report.
      admin changed the title of the reports overview from 'Reports' to 'Reports overview'.
      """
    And the report changelog reads
      """
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      admin created a new report.
      """
    And the subject changelog reads
      """
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      """
    And the metric changelog reads
      """
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      """

  Scenario: create a report, a subject, a metric, and a source
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client creates a source
    Then the changelog reads
      """
      admin added a new source to metric 'Accessibility violations' of subject 'CI-environment' in report 'New report'.
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      admin created a new report.
      admin changed the title of the reports overview from 'Reports' to 'Reports overview'.
      """
    And the report changelog reads
      """
      admin added a new source to metric 'Accessibility violations' of subject 'CI-environment' in report 'New report'.
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      admin created a new report.
      """
    And the subject changelog reads
      """
      admin added a new source to metric 'Accessibility violations' of subject 'CI-environment' in report 'New report'.
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      admin created a new subject in report 'New report'.
      """
    And the metric changelog reads
      """
      admin added a new source to metric 'Accessibility violations' of subject 'CI-environment' in report 'New report'.
      admin added a new metric to subject 'CI-environment' in report 'New report'.
      """
    And the source changelog reads
      """
      admin added a new source to metric 'Accessibility violations' of subject 'CI-environment' in report 'New report'.
      """
