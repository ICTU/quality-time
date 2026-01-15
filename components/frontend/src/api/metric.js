import { fetchServerApi } from "./fetch_server_api"

export function addMetric(subjectUuid, metricType, reload) {
    return fetchServerApi("post", `metric/new/${subjectUuid}`, { type: metricType }).then(reload)
}

export function copyMetric(metricUuid, subjectUuid, reload) {
    return fetchServerApi("post", `metric/${metricUuid}/copy/${subjectUuid}`, {}).then(reload)
}

export function moveMetric(metricUuid, subjectUuid, reload) {
    return fetchServerApi("post", `metric/${metricUuid}/move/${subjectUuid}`, {}).then(reload)
}

export function deleteMetric(metricUuid, reload) {
    return fetchServerApi("delete", `metric/${metricUuid}`, {}).then(reload)
}

export function setMetricAttribute(metricUuid, attribute, value, reload) {
    return fetchServerApi("post", `metric/${metricUuid}/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function setMetricDebt(metricUuid, value, reload) {
    return fetchServerApi("post", `metric/${metricUuid}/debt`, { accept_debt: value }).then(reload)
}

export function addMetricIssue(metricUuid, reload, showMessage) {
    const payload = { metric_url: `${globalThis.location.origin}${globalThis.location.pathname}#${metricUuid}` }
    return fetchServerApi("post", `metric/${metricUuid}/issue/new`, payload)
        .then((json) => {
            if (json.ok) {
                globalThis.open(json.issue_url)
            } else {
                showMessage(json.error)
            }
            return null
        })
        .then(reload)
}
