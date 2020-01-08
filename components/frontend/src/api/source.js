import { fetch_server_api } from "./fetch_server_api";

function add_source(metric_uuid, reload) {
    return fetch_server_api('post', `source/new/${metric_uuid}`, {}).then(reload)
}

function copy_source(source_uuid, reload) {
    return fetch_server_api('post', `source/${source_uuid}/copy`, {}).then(reload)
}

function delete_source(source_uuid, reload) {
    return fetch_server_api('delete', `source/${source_uuid}`, {}).then(reload)
}

function set_source_attribute(source_uuid, attribute, value, reload) {
    return fetch_server_api('post', `source/${source_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

function set_source_parameter(source_uuid, key, value, reload) {
    return fetch_server_api('post', `source/${source_uuid}/parameter/${key}`, { [key]: value }).then(reload)
}

function set_source_entity_attribute(metric_uuid, source_uuid, entity_key, attribute, value, reload) {
    return fetch_server_api(
        'post', `measurement/${metric_uuid}/source/${source_uuid}/entity/${entity_key}/${attribute}`,
        { [attribute]: value }).then(reload)
}

export { add_source, copy_source, delete_source, set_source_attribute, set_source_entity_attribute, set_source_parameter }
