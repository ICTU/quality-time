import { fetch_server_api } from "./fetch_server_api";
import { show_message } from '../widgets/toast';

export function add_metric(subject_uuid, metricType, reload) {
    fetch_server_api('post', `metric/new/${subject_uuid}`, { type: metricType }).then(reload)
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

export function set_metric_debt(metric_uuid, value, reload) {
    fetch_server_api('post', `metric/${metric_uuid}/debt`, { "accept_debt": value }).then(reload)
}

export function add_metric_issue(metric_uuid, reload) {
    return fetch_server_api('post', `metric/${metric_uuid}/issue/new`, {metric_url: `${window.location}#${metric_uuid}`}).then((json) => {
        if (json.ok) {
            window.open(json.issue_url)
        } else {
            show_message("error", `Error creating issue: ${json.error}`)
        }
    }).then(reload)
}
