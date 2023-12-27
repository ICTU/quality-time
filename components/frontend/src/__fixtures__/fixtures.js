import { renderHook } from '@testing-library/react';
import {
    useDateIntervalURLSearchQuery,
    useDateOrderURLSearchQuery,
    useHiddenCardsURLSearchQuery,
    useHiddenColumnsURLSearchQuery,
    useHiddenTagsURLSearchQuery,
    useMetricsToHideURLSearchQuery,
    useNrDatesURLSearchQuery,
    useSortColumnURLSearchQuery,
    useSortDirectionURLSearchQuery,
    useExpandedItemsSearchQuery,
    useShowIssueSummaryURLSearchQuery,
    useShowIssueCreationDateURLSearchQuery,
    useShowIssueUpdateDateURLSearchQuery,
    useShowIssueDueDateURLSearchQuery,
    useShowIssueReleaseURLSearchQuery,
    useShowIssueSprintURLSearchQuery
} from '../app_ui_settings';

export const datamodel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ["metric_type"] }
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    }
}

export const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject 1 title", metrics: {
                metric_uuid: {
                    name: "M1",
                    type: "metric_type",
                    tags: ["other tag"],
                    target: "1",
                    sources: {},
                    status: "target_not_met",
                    recent_measurements: [],
                    latest_measurement: {count: 1},
                    comment: "Comment 1"
                },
                metric_uuid2: {
                    name: "M2",
                    type: "metric_type",
                    tags: ["tag"],
                    target: "2",
                    issue_ids: ["ABC-42"],
                    sources: {source_uuid: {name: "Source"}},
                    status: "informative",
                    recent_measurements: [],
                    latest_measurement: {count: 2},
                    comment: "Comment 2"
                }
            }
        },
        subject_uuid2: {
            type: "subject_type", name: "Subject 2 title", metrics: {
                metric_uuid3: {
                    name: "M3", type: "metric_type", tags: [], sources: {}, recent_measurements: []
                }
            }
        }
    },
    title: "Report title"
}

export function createTestableSettings() {
    return {
        dateInterval: renderHook(() => useDateIntervalURLSearchQuery()).result.current,
        dateOrder: renderHook(() => useDateOrderURLSearchQuery()).result.current,
        hiddenCards: renderHook(() => useHiddenCardsURLSearchQuery()).result.current,
        hiddenColumns: renderHook(() => useHiddenColumnsURLSearchQuery()).result.current,
        hiddenTags: renderHook(() => useHiddenTagsURLSearchQuery()).result.current,
        metricsToHide: renderHook(() => useMetricsToHideURLSearchQuery()).result.current,
        nrDates: renderHook(() => useNrDatesURLSearchQuery()).result.current,
        showIssueCreationDate: renderHook(() => useShowIssueCreationDateURLSearchQuery()).result.current,
        showIssueSummary: renderHook(() => useShowIssueSummaryURLSearchQuery()).result.current,
        showIssueUpdateDate: renderHook(() => useShowIssueUpdateDateURLSearchQuery()).result.current,
        showIssueDueDate: renderHook(() => useShowIssueDueDateURLSearchQuery()).result.current,
        showIssueRelease: renderHook(() => useShowIssueReleaseURLSearchQuery()).result.current,
        showIssueSprint: renderHook(() => useShowIssueSprintURLSearchQuery()).result.current,
        sortColumn: renderHook(() => useSortColumnURLSearchQuery()).result.current,
        sortDirection: renderHook(() => useSortDirectionURLSearchQuery()).result.current,
        expandedItems: renderHook(() => useExpandedItemsSearchQuery()).result.current
    }
}
