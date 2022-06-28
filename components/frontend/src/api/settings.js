import { fetch_server_api } from "./fetch_server_api";

export function post_settings(settings, reload) {
    return fetch_server_api('post', `/settings/update`, settings).then(reload)
}

export function get_settings() {
    return fetch_server_api('get', `settings`, {})
}