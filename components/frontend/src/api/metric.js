import { fetch_server_api } from "./fetch_server_api";

function add_metric(subject_uuid, reload) {
    fetch_server_api('post', `metric/new/${subject_uuid}`, {}).then(reload)
}

function copy_metric(metric_uuid, reload) {
    return fetch_server_api('post', `metric/${metric_uuid}/copy`, {}).then(reload)
}

function delete_metric(metric_uuid, reload) {
    fetch_server_api('delete', `metric/${metric_uuid}`, {}).then(reload)
}

function set_metric_attribute(metric_uuid, attribute, value, reload) {
    fetch_server_api('post', `metric/${metric_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export { add_metric, copy_metric, delete_metric, set_metric_attribute }
