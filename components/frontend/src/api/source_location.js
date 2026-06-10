import { fetchServerApi } from "./fetch_server_api"

export function addSourceLocation(reportUuid, subtype, reload) {
    return fetchServerApi("post", `source_location/new/${reportUuid}`, { type: subtype }).then(reload)
}

export function deleteSourceLocation(sourceLocationUuid, reload) {
    return fetchServerApi("delete", `source_location/${sourceLocationUuid}`, {}).then(reload)
}

export function setSourceLocationAttribute(sourceLocationUuid, attribute, value, reload) {
    return fetchServerApi("post", `source_location/${sourceLocationUuid}/attribute/${attribute}`, {
        [attribute]: value,
    }).then(reload)
}

export function setSourceLocationParameter(sourceLocationUuid, key, value, reload) {
    return fetchServerApi("post", `source_location/${sourceLocationUuid}/parameter/${key}`, {
        [key]: value,
    }).then(reload)
}
