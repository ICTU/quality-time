import { renderHook } from "@testing-library/react"

import {
    allSettingsAreDefault,
    resetSettings,
    useDateIntervalURLSearchQuery,
    useDateOrderURLSearchQuery,
    useExpandedItemsSearchQuery,
    useHiddenCardsURLSearchQuery,
    useHiddenColumnsURLSearchQuery,
    useHiddenTagsURLSearchQuery,
    useLanguageURLSearchQuery,
    useMetricsToHideURLSearchQuery,
    useNrDatesURLSearchQuery,
    useShowIssueCreationDateURLSearchQuery,
    useShowIssueDueDateURLSearchQuery,
    useShowIssueReleaseURLSearchQuery,
    useShowIssueSprintURLSearchQuery,
    useShowIssueSummaryURLSearchQuery,
    useShowIssueUpdateDateURLSearchQuery,
    useSortColumnURLSearchQuery,
    useSortDirectionURLSearchQuery,
} from "../app_ui_settings"

export const dataModel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ["metric_type"] },
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] },
    },
    sources: {
        source_type: {
            name: "Source type name",
            metrics: ["metric_type"],
            parameters: { url: { type: "url", name: "URL" } },
        },
        source_type_without_location_parameters: {
            name: "Source type without location parameters",
            metrics: ["metric_type"],
            parameters: {},
        },
    },
}

export const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject 1 title",
            metrics: {
                metric_uuid: {
                    name: "M1",
                    type: "metric_type",
                    tags: ["other tag"],
                    target: "1",
                    sources: {
                        source_uuid: {
                            name: "Source",
                            type: "source_type",
                            parameters: { url: "https://source1.org" },
                        },
                    },
                    status: "target_not_met",
                    recent_measurements: [],
                    latest_measurement: { count: 1 },
                    comment: "Comment 1",
                },
                metric_uuid2: {
                    name: "M2",
                    type: "metric_type",
                    tags: ["tag"],
                    target: "2",
                    issue_ids: ["ABC-42"],
                    sources: {
                        source_uuid2: {
                            name: "Source 2",
                            type: "source_type",
                            parameters: { url: "https://sourc2.org" },
                        },
                    },
                    status: "informative",
                    recent_measurements: [],
                    latest_measurement: { count: 2 },
                    comment: "Comment 2",
                },
            },
        },
        subject_uuid2: {
            type: "subject_type",
            name: "Subject 2 title",
            metrics: {
                metric_uuid3: {
                    name: "M3",
                    type: "metric_type",
                    tags: [],
                    sources: {},
                    recent_measurements: [],
                },
            },
        },
    },
    title: "Report title",
}

function testableQuery(query) {
    return renderHook(() => query()).result.current
}

export function createTestableSettings() {
    return {
        dateInterval: testableQuery(useDateIntervalURLSearchQuery),
        dateOrder: testableQuery(useDateOrderURLSearchQuery),
        expandedItems: testableQuery(useExpandedItemsSearchQuery),
        hiddenCards: testableQuery(useHiddenCardsURLSearchQuery),
        hiddenColumns: testableQuery(useHiddenColumnsURLSearchQuery),
        hiddenTags: testableQuery(useHiddenTagsURLSearchQuery),
        language: testableQuery(useLanguageURLSearchQuery),
        metricsToHide: testableQuery(useMetricsToHideURLSearchQuery),
        nrDates: testableQuery(useNrDatesURLSearchQuery),
        showIssueCreationDate: testableQuery(useShowIssueCreationDateURLSearchQuery),
        showIssueSummary: testableQuery(useShowIssueSummaryURLSearchQuery),
        showIssueUpdateDate: testableQuery(useShowIssueUpdateDateURLSearchQuery),
        showIssueDueDate: testableQuery(useShowIssueDueDateURLSearchQuery),
        showIssueRelease: testableQuery(useShowIssueReleaseURLSearchQuery),
        showIssueSprint: testableQuery(useShowIssueSprintURLSearchQuery),
        sortColumn: testableQuery(useSortColumnURLSearchQuery),
        sortDirection: testableQuery(useSortDirectionURLSearchQuery),
        reset: function () {
            resetSettings(this)
        },
        allDefault: function () {
            return allSettingsAreDefault(this)
        },
    }
}
