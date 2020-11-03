import { fetch_server_api } from "./fetch_server_api";

function add_notification_destination(report_uuid, reload) {
    console.log("add notification destination", report_uuid, reload);
    return fetch_server_api('post', `report/${report_uuid}/notification_destination/new`, {}).then(reload)
}

function delete_notification_destination(report_uuid, destination_uuid, go_home) {
    return fetch_server_api('delete', `report/${report_uuid}/notification_destination/${destination_uuid}`, {}).then(go_home)
}

function set_notification_destination_attribute(report_uuid, destination_uuid, attribute, value, reload) {
    return fetch_server_api('post', `report/${report_uuid}/notification_destination/${destination_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export {
    add_notification_destination, delete_notification_destination, set_notification_destination_attribute}
