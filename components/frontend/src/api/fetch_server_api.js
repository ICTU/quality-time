export function api_with_report_date(api, date) {
    return date ? api + `?report_date=${date.toISOString()}` : api
}

export function fetch_server_api(method, api, body, content_type) {
    let options = {
        method: method,
        mode: "cors",
        credentials: "include",
        headers: {
            Accept: content_type || "application/json",
            "Content-Type": "application/json",
        },
    }
    if (method === "post") {
        options["body"] = JSON.stringify(body)
    }
    return fetch(`/api/internal/${api}`, options).then((response) => {
        if (response.ok) {
            return content_type ? response.blob() : response.json()
        }
        return response
    })
}
