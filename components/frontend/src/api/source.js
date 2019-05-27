import { fetch_server_api } from "./fetch_server_api";

function delete_source(report_uuid, source_uuid, reload) {
    fetch_server_api('delete', `report/${report_uuid}/source/${source_uuid}`, {}, reload)
}

export { delete_source }
