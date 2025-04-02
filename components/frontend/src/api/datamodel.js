import { apiWithReportDate, fetchServerApi } from "./fetch_server_api"

export function getDataModel(date) {
    return fetchServerApi("get", apiWithReportDate("datamodel", date))
}
