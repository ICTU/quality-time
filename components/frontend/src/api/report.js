import { api_with_report_date, fetch_server_api } from "./fetch_server_api";

function add_report(reload) {
  return fetch_server_api('post', 'report/new', {}).then(reload)
}

function copy_report(report_uuid, reload) {
  return fetch_server_api('post', `report/${report_uuid}/copy`, {}).then(reload)
}

function delete_report(report_uuid, go_home) {
  return fetch_server_api('delete', `report/${report_uuid}`, {}).then(go_home)
}

function get_reports_overview(date) {
  return fetch_server_api('get', api_with_report_date('reports_overview', date))
}

function get_reports(report_uuid, date) {
  return fetch_server_api('get', api_with_report_date(`report/${report_uuid}`, date))
}

function set_report_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function set_reports_attribute(attribute, value, reload) {
  return fetch_server_api('post', `reports_overview/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function get_report_pdf(report_uuid, query_string) {
  return fetch_server_api('get', `report/${report_uuid}/pdf${query_string}`, {}, 'application/pdf')
}

export {
  add_report, copy_report, delete_report, get_reports, get_reports_overview, get_report_pdf, set_report_attribute,
  set_reports_attribute }
