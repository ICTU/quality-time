import { fetch_server_api } from "./fetch_server_api";

export function add_notification_destination(report_uuid, reload) {
    return fetch_server_api('post', `report/${report_uuid}/notification_destination/new`, {}).then(reload)
}

export function delete_notification_destination(report_uuid, destination_uuid, reload) {
    return fetch_server_api('delete', `report/${report_uuid}/notification_destination/${destination_uuid}`, {}).then(reload)
}

export function set_notification_destination_attributes(report_uuid, destination_uuid, attributes, reload) {
    return fetch_server_api('post', `report/${report_uuid}/notification_destination/${destination_uuid}/attributes`, attributes).then(reload)
}
