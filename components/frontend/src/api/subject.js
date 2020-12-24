import { fetch_server_api } from "./fetch_server_api";

export function add_subject(report_uuid, reload) {
  return fetch_server_api('post', `subject/new/${report_uuid}`, {}).then(reload)
}

export function copy_subject(subject_uuid, report_uuid, reload) {
  return fetch_server_api('post', `subject/${subject_uuid}/copy/${report_uuid}`, {}).then(reload)
}

export function move_subject(subject_uuid, report_uuid, reload) {
  return fetch_server_api('post', `subject/${subject_uuid}/move/${report_uuid}`, {}).then(reload)
}

export function delete_subject(subject_uuid, reload) {
  return fetch_server_api('delete', `subject/${subject_uuid}`, {}).then(reload)
}

export function set_subject_attribute(subject_uuid, attribute, value, reload) {
  return fetch_server_api('post', `subject/${subject_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export function get_subject_measurements(subject_uuid, date) {
  return fetch_server_api('get', `subject/${subject_uuid}/measurements`, date)
}
