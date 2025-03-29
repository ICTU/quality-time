import { fetchServerApi } from "./fetch_server_api"

export function addSource(metricUuid, subtype, reload) {
    return fetchServerApi("post", `source/new/${metricUuid}`, { type: subtype }).then(reload)
}

export function copySource(sourceUuid, metricUuid, reload) {
    return fetchServerApi("post", `source/${sourceUuid}/copy/${metricUuid}`, {}).then(reload)
}

export function moveSource(sourceUuid, metricUuid, reload) {
    return fetchServerApi("post", `source/${sourceUuid}/move/${metricUuid}`, {}).then(reload)
}

export function deleteSource(sourceUuid, reload) {
    return fetchServerApi("delete", `source/${sourceUuid}`, {}).then(reload)
}

export function setSourceAttribute(sourceUuid, attribute, value, reload) {
    return fetchServerApi("post", `source/${sourceUuid}/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function setSourceParameter(sourceUuid, key, value, editScope, reload) {
    return fetchServerApi("post", `source/${sourceUuid}/parameter/${key}`, {
        [key]: value,
        edit_scope: editScope,
    }).then(reload)
}

export function setSourceEntityAttribute(metricUuid, sourceUuid, entityKey, attribute, value, reload) {
    return fetchServerApi("post", `measurement/${metricUuid}/source/${sourceUuid}/entity/${entityKey}/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}
