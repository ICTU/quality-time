import { api_with_report_date, fetch_server_api } from "./fetch_server_api";

export function add_report(reload) {
  return fetch_server_api('post', 'report/new', {}).then(reload)
}

export function copy_report(report_uuid, reload) {
  return fetch_server_api('post', `report/${report_uuid}/copy`, {}).then(reload)
}

export function delete_report(report_uuid, go_home) {
  return fetch_server_api('delete', `report/${report_uuid}`, {}).then(go_home)
}

export function get_reports_overview(date) {
  return fetch_server_api('get', api_with_report_date('reports_overview', date))
}

export function get_report(report_uuid, date) {
  return fetch_server_api('get', api_with_report_date(`report/${report_uuid}`, date))
}

export function set_report_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export function set_report_issue_tracker_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/issue_tracker/${attribute}`, { [attribute]: value }).then(reload)
}

export function set_reports_attribute(attribute, value, reload) {
  return fetch_server_api('post', `reports_overview/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export function get_report_pdf(report_uuid, query_string) {
  return fetch_server_api('get', `report/${report_uuid}/pdf${query_string}`, {}, 'application/pdf')
}

export function get_report_issue_tracker_options(report_uuid) {
    return fetch_server_api('get', `report/${report_uuid}/issue_tracker/options`)
}

export function get_report_issue_tracker_suggestions(report_uuid, query) {
    return fetch_server_api('get', `report/${report_uuid}/issue_tracker/suggestions/${query}`)
}
