import PropTypes from 'prop-types';

export const datePropType = PropTypes.instanceOf(Date)

export const optionalDatePropType = datePropType

export const datesPropType = PropTypes.arrayOf(datePropType)

export const stringsPropType = PropTypes.arrayOf(PropTypes.string)

export const boolURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    set: PropTypes.func,
    value: PropTypes.bool
})

export const integerURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    set: PropTypes.func,
    value: PropTypes.number
})

export const stringURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    set: PropTypes.func,
    value: PropTypes.string
})

export const stringsURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    toggle: PropTypes.func,
    value: stringsPropType
})

export const sortDirectionPropType = PropTypes.oneOf(["ascending", "descending"])

export const sortDirectionURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    set: PropTypes.func,
    value: sortDirectionPropType
})

export const metricsToHidePropType = PropTypes.oneOf(["none", "all", "no_action_needed"])

export const metricsToHideURLSearchQueryPropType = PropTypes.shape({
    isDefault: PropTypes.func,
    reset: PropTypes.func,
    set: PropTypes.func,
    value: metricsToHidePropType
})

export const settingsPropType = PropTypes.shape({
    dateInterval: integerURLSearchQueryPropType,
    dateOrder: sortDirectionURLSearchQueryPropType,
    hiddenColumns: stringsURLSearchQueryPropType,
    hiddenTags: stringsURLSearchQueryPropType,
    metricsToHide: metricsToHideURLSearchQueryPropType,
    nrDates: integerURLSearchQueryPropType,
    showIssueCreationDate: boolURLSearchQueryPropType,
    showIssueDueDate: boolURLSearchQueryPropType,
    showIssueRelease: boolURLSearchQueryPropType,
    showIssueSprint: boolURLSearchQueryPropType,
    showIssueSummary: boolURLSearchQueryPropType,
    showIssueUpdateDate: boolURLSearchQueryPropType,
    sortColumn: stringURLSearchQueryPropType,
    sortDirection: sortDirectionURLSearchQueryPropType,
    visibleDetailsTabs: stringsURLSearchQueryPropType
})

export const entityStatusPropType = PropTypes.oneOf(["unconfirmed", "confirmed", "fixed", "false_positive", "wont_fix"])

export const entityPropType = PropTypes.shape({
    key: PropTypes.string,
})

const entityAttributePropType = PropTypes.shape({
    key: PropTypes.string,
})

export const entityAttributesPropType = PropTypes.arrayOf(entityAttributePropType)

export const issueStatusPropType = PropTypes.shape({
    connection_error: PropTypes.string,
    created: PropTypes.string,
    duedate: PropTypes.string,
    issue_id: PropTypes.string,
    landing_url: PropTypes.string,
    parse_error: PropTypes.string,
    release_name: PropTypes.string,
    release_released: PropTypes.bool,
    sprint_enddate: PropTypes.string,
    sprint_name: PropTypes.string,
    sprint_state: PropTypes.string,
    status_category: PropTypes.oneOf(["todo", "doing", "done"]),
    summary: PropTypes.string,
    updated: PropTypes.string
})

export const sourcePropType = PropTypes.shape({
    entities: PropTypes.array,
    entity_user_data: PropTypes.object,
    source_uuid: PropTypes.string,
})

export const metricPropType = PropTypes.shape({
    accept_debt: PropTypes.bool,
    debt_end_date: PropTypes.string,
    evaluate_targets: PropTypes.bool,
    issue_ids: stringsPropType,
    issue_status: PropTypes.arrayOf(issueStatusPropType)
})

export const reportPropType = PropTypes.shape({
    issue_tracker: PropTypes.object,
})

export const reportsPropType = PropTypes.arrayOf(reportPropType)

export const uiModePropType = PropTypes.oneOf(["dark", "light", "follow_os"])
