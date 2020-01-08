import { fetch_server_api } from "./fetch_server_api";

export function login(username, password) {
    return fetch_server_api('post', 'login', { username: username, password: password })
}

export function logout() {
    return fetch_server_api('post', 'logout', {})
}
