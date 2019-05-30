import { fetch_server_api } from "./fetch_server_api";

function login(username, password) {
    return fetch_server_api('post', 'login', { username: username, password: password })
}

function logout() {
    return fetch_server_api('post', 'logout', {})
}

export { login, logout }
