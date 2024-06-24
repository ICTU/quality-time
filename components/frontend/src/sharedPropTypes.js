import {
    array,
    arrayOf,
    bool,
    element,
    func,
    instanceOf,
    node,
    number,
    object,
    objectOf,
    oneOf,
    oneOfType,
    shape,
    string,
} from "prop-types"

export const childrenPropType = node

export const datePropType = instanceOf(Date)

export const optionalDatePropType = datePropType

export const datesPropType = arrayOf(datePropType)

export const stringsPropType = arrayOf(string)

export const boolURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    set: func,
    value: bool,
})

export const integerURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    set: func,
    value: number,
})

export const stringURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    set: func,
    value: string,
})

export const stringsURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    toggle: func,
    value: stringsPropType,
})

export const labelPropType = oneOfType([object, string])

export const popupContentPropType = oneOfType([element, string])

export const permissionsPropType = arrayOf(string)

export const directionPropType = oneOf(["<", ">"])

export const sortDirectionPropType = oneOf(["ascending", "descending"])

export const sortDirectionURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    set: func,
    value: sortDirectionPropType,
})

export const hiddenCardsPropType = oneOf(["action_required", "reports", "subjects", "tags", "issues", "legend"])

export const metricsToHidePropType = oneOf(["all", "none", "no_action_required", "no_issues"])

export const metricsToHideURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    set: func,
    value: metricsToHidePropType,
})

export const settingsPropType = shape({
    dateInterval: integerURLSearchQueryPropType,
    dateOrder: sortDirectionURLSearchQueryPropType,
    expandedItems: stringsURLSearchQueryPropType,
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
})

export const entityStatusPropType = oneOf(["unconfirmed", "confirmed", "fixed", "false_positive", "wont_fix"])

export const entityPropType = shape({
    key: string,
})

export const entityAttributePropType = shape({
    key: string,
})

export const entityAttributesPropType = arrayOf(entityAttributePropType)

export const issueStatusPropType = shape({
    connection_error: string,
    created: string,
    duedate: string,
    issue_id: string,
    landing_url: string,
    parse_error: string,
    release_name: string,
    release_released: bool,
    sprint_enddate: string,
    sprint_name: string,
    sprint_state: string,
    status_category: oneOf(["todo", "doing", "done"]),
    summary: string,
    updated: string,
})

export const measurementSourcePropType = shape({
    connection_error: string,
    parse_error: string,
})

export const measurementPropType = shape({
    sources: arrayOf(measurementSourcePropType),
})

export const measurementsPropType = arrayOf(measurementPropType)

export const sourcePropType = shape({
    entities: array,
    entity_user_data: object,
    source_uuid: string,
})

export const sourceTypePropType = shape({
    description: string,
    documentation: object,
    name: string,
})

export const subjectPropType = shape({
    type: string,
})

export const scalePropType = oneOf(["count", "percentage", "version_number"])

export const metricPropType = shape({
    accept_debt: bool,
    debt_end_date: string,
    evaluate_targets: bool,
    issue_ids: stringsPropType,
    issue_status: arrayOf(issueStatusPropType),
    scale: scalePropType,
    tags: stringsPropType,
})

export const metricsPropType = arrayOf(metricPropType)

export const metricTypePropType = shape({
    description: string,
    documentation: string,
    name: string,
})

// Construct a recursive prop type for the subject type
const subjectTypeShape = {
    description: string,
    metrics: stringsPropType,
    name: string,
}
subjectTypeShape.subjects = arrayOf(shape(subjectTypeShape))
export const subjectTypePropType = shape(subjectTypeShape)

export const dataModelPropType = shape({
    metrics: objectOf(metricTypePropType),
    sources: objectOf(sourceTypePropType),
    subjects: objectOf(subjectTypePropType),
})

export const destinationPropType = shape({
    name: string,
    webhook: string,
})

export const reportPropType = shape({
    comment: string,
    desired_response_times: object,
    issue_tracker: object,
    report_uuid: string,
})

export const reportsPropType = arrayOf(reportPropType)

export const reportsOverviewPropType = shape({
    comment: string,
    permissions: object,
    title: string,
    subtitle: string,
})

export const uiModePropType = oneOf(["dark", "light", "follow_os"])
