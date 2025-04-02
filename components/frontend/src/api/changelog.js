import { fetchServerApi } from "./fetch_server_api"

export function getChangelog(nrChanges, uuids) {
    const entityTypes = ["source", "metric", "subject", "report"]

    for (const entityType of entityTypes) {
        const uuidKey = `${entityType}_uuid`
        if (Object.keys(uuids).includes(uuidKey)) {
            return fetchServerApi("get", `changelog/${entityType}/${uuids[uuidKey]}/${nrChanges}`)
        }
    }
    return fetchServerApi("get", `changelog/${nrChanges}`)
}
