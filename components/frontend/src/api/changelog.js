import { fetch_server_api } from "./fetch_server_api";

export function get_changelog(nr_changes, uuids) {
    if (Object.keys(uuids).includes("source_uuid")) {
        return fetch_server_api('get', `changelog/source/${uuids.source_uuid}/${nr_changes}`)
    }
    if (Object.keys(uuids).includes("metric_uuid")) {
        return fetch_server_api('get', `changelog/metric/${uuids.metric_uuid}/${nr_changes}`)
    }
    if (Object.keys(uuids).includes("subject_uuid")) {
        return fetch_server_api('get', `changelog/subject/${uuids.subject_uuid}/${nr_changes}`)
    }
    if (Object.keys(uuids).includes("report_uuid")) {
        return fetch_server_api('get', `changelog/report/${uuids.report_uuid}/${nr_changes}`)
    }
    return fetch_server_api('get', `changelog/${nr_changes}`)
}
