import { fetch_server_api } from "./fetch_server_api";

function add_report(reload) {
  fetch_server_api('post', 'report/new', {}, reload)
}

function delete_report(report_uuid, go_home) {
  fetch_server_api('delete', `report/${report_uuid}`, {}, go_home)
}

function set_report_attribute(report_uuid, attribute, value, reload) {
    fetch_server_api('post', `report/${report_uuid}/${attribute}`, { [attribute]: value }, reload)
}

export { add_report, delete_report, set_report_attribute }
