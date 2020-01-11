import { fetch_server_api } from "./fetch_server_api";

export function add_source(metric_uuid, reload) {
    return fetch_server_api('post', `source/new/${metric_uuid}`, {}).then(reload)
}

export function copy_source(source_uuid, reload) {
    return fetch_server_api('post', `source/${source_uuid}/copy`, {}).then(reload)
}

export function move_source(source_uuid, metric_uuid, reload) {
    return fetch_server_api('post', `source/${source_uuid}/move/${metric_uuid}`, {}).then(reload)
}

export function delete_source(source_uuid, reload) {
    return fetch_server_api('delete', `source/${source_uuid}`, {}).then(reload)
}

export function set_source_attribute(source_uuid, attribute, value, reload) {
    return fetch_server_api('post', `source/${source_uuid}/attribute/${attribute}`, { [attribute]: value }).then(reload)
}

export function set_source_parameter(source_uuid, key, value, reload) {
    return fetch_server_api('post', `source/${source_uuid}/parameter/${key}`, { [key]: value }).then(reload)
}

export function set_source_entity_attribute(metric_uuid, source_uuid, entity_key, attribute, value, reload) {
    return fetch_server_api(
        'post', `measurement/${metric_uuid}/source/${source_uuid}/entity/${entity_key}/${attribute}`,
        { [attribute]: value }).then(reload)
}
