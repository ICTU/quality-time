import { fetchServerApi } from "./fetch_server_api"

export function addSubject(reportUuid, subjectType, reload) {
    return fetchServerApi("post", `subject/new/${reportUuid}`, { type: subjectType }).then(reload)
}

export function copySubject(subjectUuid, reportUuid, reload) {
    return fetchServerApi("post", `subject/${subjectUuid}/copy/${reportUuid}`, {}).then(reload)
}

export function moveSubject(subjectUuid, reportUuid, reload) {
    return fetchServerApi("post", `subject/${subjectUuid}/move/${reportUuid}`, {}).then(reload)
}

export function deleteSubject(subjectUuid, reload) {
    return fetchServerApi("delete", `subject/${subjectUuid}`, {}).then(reload)
}

export function setSubjectAttribute(subjectUuid, attribute, value, reload) {
    return fetchServerApi("post", `subject/${subjectUuid}/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}
