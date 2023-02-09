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

function get_reports_overview_measurements(date, minDate) {
    const minReportDate = minDate.toISOString().split("T")[0] + "T00:00:00.000Z"; // Ignore the time so we get all measurements for the min date
    const api = api_with_report_date("reports_overview/measurements", date);
    const sep = api.indexOf("?") < 0 ? "?" : "&";
    return fetch_server_api('get', api + `${sep}min_report_date=${minReportDate}`);
}

function get_report_measurements(report_uuid, date, minDate) {
    const minReportDate = minDate.toISOString().split("T")[0] + "T00:00:00.000Z"; // Ignore the time so we get all measurements for the min date
    const api = api_with_report_date(`report/${report_uuid}/measurements`, date);
    const sep = api.indexOf("?") < 0 ? "?" : "&";
    return fetch_server_api('get', api + `${sep}min_report_date=${minReportDate}`);
}

function set_report_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function set_report_issue_tracker_attribute(report_uuid, attribute, value, reload) {
  return fetch_server_api('post', `report/${report_uuid}/issue_tracker/${attribute}`, { [attribute]: value }).then(reload)
}

function set_reports_attribute(attribute, value, reload) {
  return fetch_server_api('post', `reports_overview/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function get_report_pdf(report_uuid, query_string) {
  return fetch_server_api('get', `report/${report_uuid}/pdf${query_string}`, {}, 'application/pdf')
}

function get_report_issue_tracker_options(report_uuid) {
    return fetch_server_api('get', `report/${report_uuid}/issue_tracker/options`)
}

function get_report_issue_tracker_suggestions(report_uuid, query) {
    return fetch_server_api('get', `report/${report_uuid}/issue_tracker/suggestions/${query}`)
}

export {
  add_report, copy_report, delete_report, get_reports, get_reports_overview, get_reports_overview_measurements,
  get_report_pdf, set_report_attribute, set_report_issue_tracker_attribute, set_reports_attribute,
  get_report_issue_tracker_options, get_report_issue_tracker_suggestions, get_report_measurements
}
