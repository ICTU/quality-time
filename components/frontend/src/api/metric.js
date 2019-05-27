import { fetch_server_api } from "./fetch_server_api";

function delete_metric(report_uuid, metric_uuid, reload) {
    fetch_server_api('delete', `report/${report_uuid}/metric/${metric_uuid}`, {}, reload)
  }

function set_metric_attribute(report_uuid, metric_uuid, attribute, value, reload) {
    fetch_server_api('post', `report/${report_uuid}/metric/${metric_uuid}/${attribute}`, { [attribute]: value }, reload)
}

export { delete_metric, set_metric_attribute }
