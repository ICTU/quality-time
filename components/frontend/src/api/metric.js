import { fetch_server_api } from "./fetch_server_api";

function delete_metric(report_uuid, metric_uuid, reload) {
    fetch_server_api('delete', `report/${report_uuid}/metric/${metric_uuid}`, {}, reload)
  }

export { delete_metric }
