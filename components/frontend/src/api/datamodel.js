import { api_with_report_date, fetch_server_api } from "./fetch_server_api"

export function getDataModel(date) {
    return fetch_server_api("get", api_with_report_date("datamodel", date))
}
