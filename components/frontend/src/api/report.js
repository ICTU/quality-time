import { fetch_server_api } from "./fetch_server_api";

function add_report(reload) {
  return fetch_server_api('post', 'report/new', {}).then(reload)
}

function delete_report(report_uuid, go_home) {
  return fetch_server_api('delete', `report/${report_uuid}`, {}).then(go_home)
}

function set_report_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/${attribute}`, { [attribute]: value }).then(reload)
}

export { add_report, delete_report, set_report_attribute }
