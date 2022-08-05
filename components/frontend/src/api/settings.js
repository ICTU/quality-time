import { fetch_server_api } from "./fetch_server_api";

export function put_settings(settings) {
    return fetch_server_api('put', 'settings', settings)
}

export function get_settings() {
    return fetch_server_api('get', 'settings', {})
} 