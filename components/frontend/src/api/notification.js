import { fetchServerApi } from "./fetch_server_api"

export function addNotificationDestination(reportUuid, reload) {
    const reportUrl = globalThis.location.href.split("?")[0]
    return fetchServerApi("post", `report/${reportUuid}/notification_destination/new`, {
        report_url: reportUrl,
    }).then(reload)
}

export function deleteNotificationDestination(reportUuid, destinationUuid, reload) {
    return fetchServerApi("delete", `report/${reportUuid}/notification_destination/${destinationUuid}`, {}).then(reload)
}

export function setNotificationDestinationAttributes(reportUuid, destinationUuid, attributes, reload) {
    return fetchServerApi(
        "post",
        `report/${reportUuid}/notification_destination/${destinationUuid}/attributes`,
        attributes,
    ).then(reload)
}
