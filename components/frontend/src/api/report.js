import { fetch_server_api } from "./fetch_server_api";

function add_report(reload) {
  return fetch_server_api('post', 'report/new', {}).then(reload)
}

function copy_report(report_uuid, reload) {
  return fetch_server_api('post', `report/${report_uuid}/copy`, {}).then(reload)
}

function delete_report(report_uuid, go_home) {
  return fetch_server_api('delete', `report/${report_uuid}`, {}).then(go_home)
}

function get_reports(date) {
  return fetch_server_api('get', `reports?report_date=${date.toISOString()}`)
}

function get_tag_report(tag, date) {
  return fetch_server_api('get', `tagreport/${tag}?report_date=${date.toISOString()}`)
}

function set_report_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function set_reports_attribute(attribute, value, reload) {
  return fetch_server_api('post', `reports/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function get_report_pdf(report_uuid, query_string) {
  return fetch_server_api('get', `report/${report_uuid}/pdf${query_string}`, {}, 'application/pdf')
}

export {
  add_report, copy_report, delete_report, get_reports, get_report_pdf, get_tag_report, set_report_attribute,
  set_reports_attribute }
