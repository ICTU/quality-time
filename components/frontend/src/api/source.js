import { fetch_server_api } from "./fetch_server_api";

function add_source(report_uuid, metric_uuid, reload) {
    fetch_server_api('post', `report/${report_uuid}/metric/${metric_uuid}/source/new`, {}, reload)
}

function delete_source(report_uuid, source_uuid, reload) {
    fetch_server_api('delete', `report/${report_uuid}/source/${source_uuid}`, {}, reload)
}

function set_source_attribute(report_uuid, source_uuid, attribute, value, reload) {
    fetch_server_api('post', `report/${report_uuid}/source/${source_uuid}/${attribute}`, { [attribute]: value }, reload)
}

export { add_source, delete_source, set_source_attribute }
