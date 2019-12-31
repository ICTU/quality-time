import { fetch_server_api } from "./fetch_server_api";

function add_metric(report_uuid, subject_uuid, reload) {
    fetch_server_api('post', `report/${report_uuid}/subject/${subject_uuid}/metric/new`, {}).then(reload)
}

function copy_metric(report_uuid, metric_uuid, reload) {
    return fetch_server_api('post', `report/${report_uuid}/metric/${metric_uuid}/copy`, {}).then(reload)
}

function delete_metric(report_uuid, metric_uuid, reload) {
    fetch_server_api('delete', `report/${report_uuid}/metric/${metric_uuid}`, {}).then(reload)
}

function set_metric_attribute(report_uuid, metric_uuid, attribute, value, reload) {
    fetch_server_api('post', `report/${report_uuid}/metric/${metric_uuid}/${attribute}`, { [attribute]: value }).then(reload)
}

export { add_metric, copy_metric, delete_metric, set_metric_attribute }
