import { fetch_server_api } from "./fetch_server_api";

export function get_datamodel(date) {
    return fetch_server_api('get', `datamodel?report_date=${date.toISOString()}`, {})
}
