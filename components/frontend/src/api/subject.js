import { fetch_server_api } from "./fetch_server_api";

function add_subject(report_uuid, reload) {
  fetch_server_api('post', `report/${report_uuid}/subject/new`, {}, reload)
}

function delete_subject(report_uuid, subject_uuid, reload) {
  fetch_server_api('delete', `report/${report_uuid}/subject/${subject_uuid}`, {}, reload)
}

function set_subject_attribute(report_uuid, subject_uuid, attribute, value, reload) {
  fetch_server_api('post', `report/${report_uuid}/subject/${subject_uuid}/${attribute}`, { [attribute]: value }, reload)
}

export { add_subject, delete_subject, set_subject_attribute }