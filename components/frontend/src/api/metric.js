import { fetch_server_api } from "./fetch_server_api";

export function add_metric(subject_uuid, reload) {
    fetch_server_api('post', `metric/new/${subject_uuid}`, {}).then(reload)
}

export function copy_metric(metric_uuid, subject_uuid, reload) {
    return fetch_server_api('post', `metric/${metric_uuid}/copy/${subject_uuid}`, {}).then(reload)
}

export function move_metric(metric_uuid, subject_uuid, reload) {
    return fetch_server_api('post', `metric/${metric_uuid}/move/${subject_uuid}`, {}).then(reload)
}

export function delete_metric(metric_uuid, reload) {
    fetch_server_api('delete', `metric/${metric_uuid}`, {}).then(reload)
}

export function set_metric_attribute(metric_uuid, attribute, value, reload) {
    fetch_server_api('post', `metric/${metric_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export function get_tracker_issue_status(metric_uuid, setState) {
    fetch_server_api('get', `metric/${metric_uuid}/tracker_issue_status`).then((json) => setState({loading:false, ...json}))
}
