import {
    useArrayURLSearchQuery,
    useBooleanURLSearchQuery,
    useIntegerMappingURLSearchQuery,
    useIntegerURLSearchQuery,
    useStringURLSearchQuery,
} from "./hooks/url_search_query"
import { adapterLocale } from "./locale"

function urlSearchQueryKey(key, reportUuid) {
    // Make the settings changeable per report (and separately for the reports overview) by adding the report UUID as
    // postfix to the settings key:
    return key + (reportUuid ? `_${reportUuid}` : "")
}

export function useDateIntervalURLSearchQuery(reportUuid, defaultValue = 7) {
    return useIntegerURLSearchQuery(urlSearchQueryKey("date_interval", reportUuid), defaultValue)
}

export function useDateOrderURLSearchQuery(reportUuid, defaultValue = "descending") {
    return useStringURLSearchQuery(urlSearchQueryKey("date_order", reportUuid), defaultValue)
}

export function useHiddenCardsURLSearchQuery(reportUuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("hidden_cards", reportUuid))
}

export function useHiddenColumnsURLSearchQuery(reportUuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("hidden_columns", reportUuid))
}

export function useHideEmptyColumnsURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("hide_empty_columns", reportUuid))
}

export function useHiddenTagsURLSearchQuery(reportUuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("hidden_tags", reportUuid))
}

export function useLanguageURLSearchQuery() {
    return useStringURLSearchQuery("language", adapterLocale(navigator.language))
}

export function useMetricsToHideURLSearchQuery(reportUuid) {
    return useStringURLSearchQuery(urlSearchQueryKey("metrics_to_hide", reportUuid), reportUuid === "" ? "all" : "none")
}

export function useNrDatesURLSearchQuery(reportUuid, defaultValue = 1) {
    return useIntegerURLSearchQuery(urlSearchQueryKey("nr_dates", reportUuid), defaultValue)
}

export function useSortColumnURLSearchQuery(reportUuid, defaultValue = "") {
    return useStringURLSearchQuery(urlSearchQueryKey("sort_column", reportUuid), defaultValue)
}

export function useSortDirectionURLSearchQuery(reportUuid, defaultValue = "ascending") {
    return useStringURLSearchQuery(urlSearchQueryKey("sort_direction", reportUuid), defaultValue)
}

export function useExpandedItemsSearchQuery(reportUuid) {
    // Use useIntegerMappingURLSearchQuery to handle expanded items and tabs. Key is the item, value is the tab index.
    return useIntegerMappingURLSearchQuery(urlSearchQueryKey("expanded", reportUuid))
}

export function useShowIssueSummaryURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_summary", reportUuid))
}

export function useShowIssueCreationDateURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_creation_date", reportUuid))
}

export function useShowIssueUpdateDateURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_update_date", reportUuid))
}

export function useShowIssueDueDateURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_due_date", reportUuid))
}

export function useShowIssueReleaseURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_release", reportUuid))
}

export function useShowIssueSprintURLSearchQuery(reportUuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_sprint", reportUuid))
}

export function useSettings(reportUuid) {
    return {
        dateInterval: useDateIntervalURLSearchQuery(reportUuid),
        dateOrder: useDateOrderURLSearchQuery(reportUuid),
        expandedItems: useExpandedItemsSearchQuery(reportUuid),
        hiddenCards: useHiddenCardsURLSearchQuery(reportUuid),
        hiddenColumns: useHiddenColumnsURLSearchQuery(reportUuid),
        hideEmptyColumns: useHideEmptyColumnsURLSearchQuery(reportUuid),
        hiddenTags: useHiddenTagsURLSearchQuery(reportUuid),
        language: useLanguageURLSearchQuery(),
        metricsToHide: useMetricsToHideURLSearchQuery(reportUuid),
        nrDates: useNrDatesURLSearchQuery(reportUuid),
        showIssueSummary: useShowIssueSummaryURLSearchQuery(reportUuid),
        showIssueCreationDate: useShowIssueCreationDateURLSearchQuery(reportUuid),
        showIssueUpdateDate: useShowIssueUpdateDateURLSearchQuery(reportUuid),
        showIssueDueDate: useShowIssueDueDateURLSearchQuery(reportUuid),
        showIssueRelease: useShowIssueReleaseURLSearchQuery(reportUuid),
        showIssueSprint: useShowIssueSprintURLSearchQuery(reportUuid),
        sortColumn: useSortColumnURLSearchQuery(reportUuid),
        sortDirection: useSortDirectionURLSearchQuery(reportUuid),
        reset: function () {
            resetSettings(this)
        },
        allDefault: function () {
            return allSettingsAreDefault(this)
        },
    }
}

export function resetSettings(settings) {
    settings.dateInterval.reset()
    settings.dateOrder.reset()
    settings.expandedItems.reset()
    settings.hiddenCards.reset()
    settings.hiddenColumns.reset()
    settings.hiddenTags.reset()
    settings.hideEmptyColumns.reset()
    settings.language.reset()
    settings.metricsToHide.reset()
    settings.nrDates.reset()
    settings.showIssueCreationDate.reset()
    settings.showIssueDueDate.reset()
    settings.showIssueRelease.reset()
    settings.showIssueSprint.reset()
    settings.showIssueSummary.reset()
    settings.showIssueUpdateDate.reset()
    settings.sortColumn.reset()
    settings.sortDirection.reset()
}

export function allSettingsAreDefault(settings) {
    return (
        settings.dateInterval.isDefault() &&
        settings.dateOrder.isDefault() &&
        settings.expandedItems.isDefault() &&
        settings.hiddenCards.isDefault() &&
        settings.hiddenColumns.isDefault() &&
        settings.hiddenTags.isDefault() &&
        settings.hideEmptyColumns.isDefault() &&
        settings.language.isDefault() &&
        settings.metricsToHide.isDefault() &&
        settings.nrDates.isDefault() &&
        settings.showIssueCreationDate.isDefault() &&
        settings.showIssueDueDate.isDefault() &&
        settings.showIssueRelease.isDefault() &&
        settings.showIssueSprint.isDefault() &&
        settings.showIssueSummary.isDefault() &&
        settings.showIssueUpdateDate.isDefault() &&
        settings.sortColumn.isDefault() &&
        settings.sortDirection.isDefault()
    )
}
