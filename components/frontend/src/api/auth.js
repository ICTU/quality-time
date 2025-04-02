import { fetchServerApi } from "./fetch_server_api"

export function login(username, password) {
    return fetchServerApi("post", "login", { username: username, password: password })
}

export function logout() {
    return fetchServerApi("post", "logout", {})
}
