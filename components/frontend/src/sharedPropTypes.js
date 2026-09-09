import {
    array,
    arrayOf,
    bool,
    element,
    func,
    instanceOf,
    number,
    object,
    objectOf,
    oneOf,
    oneOfType,
    shape,
    string,
} from "prop-types"

export { node as childrenPropType } from "prop-types"

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

export const mappingURLSearchQueryPropType = shape({
    isDefault: func,
    reset: func,
    getItem: func,
    setItem: func,
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

export const loadingPropType = oneOf(["failed", "loaded", "loading"])

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
    entitySortColumn: mappingURLSearchQueryPropType,
    entitySortDirection: mappingURLSearchQueryPropType,
    expandedItems: stringsURLSearchQueryPropType,
    hiddenColumns: stringsURLSearchQueryPropType,
    hideIgnoredEntities: stringsURLSearchQueryPropType,
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

// The user data of one measurement entity, as passed to the components that show and edit it
export const entityUserDataPropType = shape({
    status: entityStatusPropType,
    statusEndDate: string,
    rationale: string,
})

export const entityAttributePropType = shape({
    key: string,
})

export const entityAttributesPropType = arrayOf(entityAttributePropType)

export const entityAttributeTypePropType = oneOf([
    "boolean",
    "date",
    "datetime",
    "integer",
    "integer_percentage",
    "float",
    "minutes",
    "text",
])

export const alignmentPropType = oneOf(["center", "left", "right"])

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

// The user data of the measurement entities of one source, as stored in a measurement, keyed by entity key.
// The API-server writes the excluded and exclusion end date attributes, but the frontend does not read them yet,
// see https://github.com/ICTU/quality-time/issues/9856.
const measurementEntityUserDataPropType = objectOf(
    shape({
        excluded: bool,
        exclusion_end_date: string,
        orphaned_since: string,
        rationale: string,
        status: entityStatusPropType,
        status_end_date: string,
    }),
)

export const measurementSourcePropType = shape({
    entity_user_data: measurementEntityUserDataPropType,
    connection_error: string,
    parse_error: string,
})

export const measurementPropType = shape({
    sources: arrayOf(measurementSourcePropType),
})

export const measurementsPropType = arrayOf(measurementPropType)

export const sourcePropType = shape({
    entities: array,
    entity_user_data: measurementEntityUserDataPropType,
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

export const targetType = oneOf(["debt_target", "near_target", "target"])

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

export const uiModePropType = oneOf(["dark", "light", "system"])

export const snackbarMessagePropType = shape({
    severity: oneOf(["error", "info", "success", "warning"]),
    title: string,
    description: string,
})

export const snackbarMessagesPropType = arrayOf(snackbarMessagePropType)

export const availabilityMessagePropType = shape({
    status_code: number,
    reason: string,
    parameter_key: string,
    source_uuid: string,
})
