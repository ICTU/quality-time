import { apiWithReportDate, fetchServerApi } from "./fetch_server_api"

export function addReport(reload) {
    return fetchServerApi("post", "report/new", {}).then(reload)
}

export function importReport(report, reload) {
    return fetchServerApi("post", "report/import", report).then(reload)
}

export function copyReport(reportUuid, reload) {
    return fetchServerApi("post", `report/${reportUuid}/copy`, {}).then(reload)
}

export function deleteReport(reportUuid, openReportsOverview) {
    return fetchServerApi("delete", `report/${reportUuid}`, {}).then(openReportsOverview)
}

export function getReportsOverview(date) {
    return fetchServerApi("get", apiWithReportDate("reports_overview", date))
}

export function getReport(reportUuid, date) {
    return fetchServerApi("get", apiWithReportDate(`report/${reportUuid}`, date))
}

export function setReportAttribute(reportUuid, attribute, value, reload) {
    return fetchServerApi("post", `report/${reportUuid}/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function setReportIssueTrackerAttribute(reportUuid, attribute, value, reload) {
    return fetchServerApi("post", `report/${reportUuid}/issue_tracker/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function setReportsAttribute(attribute, value, reload) {
    return fetchServerApi("post", `reports_overview/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function getReportPdf(reportUuid, queryString) {
    const endpoint = (reportUuid ? `report/${reportUuid}` : "reports_overview") + `/pdf${queryString}`
    return fetchServerApi("get", endpoint, {}, "application/pdf")
}

export function getReportIssueTrackerOptions(reportUuid) {
    return fetchServerApi("get", `report/${reportUuid}/issue_tracker/options`)
}

export function getReportIssueTrackerSuggestions(reportUuid, query) {
    return fetchServerApi("get", `report/${reportUuid}/issue_tracker/suggestions/${query}`)
}

export function deleteTag(reportUuid, tag, reload) {
    return fetchServerApi("delete", `report/${reportUuid}/tag/${tag}`).then(reload)
}

export function renameTag(reportUuid, tag, newTag, reload) {
    return fetchServerApi("post", `report/${reportUuid}/tag/${tag}`, { tag: newTag }).then(reload)
}
