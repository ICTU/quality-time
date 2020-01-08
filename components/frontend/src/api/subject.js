import { fetch_server_api } from "./fetch_server_api";

function add_subject(report_uuid, reload) {
  return fetch_server_api('post', `subject/new/${report_uuid}`, {}).then(reload)
}

function copy_subject(subject_uuid, reload) {
  return fetch_server_api('post', `subject/${subject_uuid}/copy`, {}).then(reload)
}

function delete_subject(subject_uuid, reload) {
  return fetch_server_api('delete', `subject/${subject_uuid}`, {}).then(reload)
}

function set_subject_attribute(subject_uuid, attribute, value, reload) {
  return fetch_server_api('post', `subject/${subject_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export { add_subject, copy_subject, delete_subject, set_subject_attribute }
