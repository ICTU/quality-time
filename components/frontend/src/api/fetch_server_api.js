export function apiWithReportDate(api, date) {
    return date ? api + `?report_date=${date.toISOString()}` : api
}

export function fetchServerApi(method, api, body, contentType) {
    let options = {
        method: method,
        mode: "cors",
        credentials: "include",
        headers: {
            Accept: contentType || "application/json",
            "Content-Type": "application/json",
        },
    }
    if (method === "post") {
        options["body"] = JSON.stringify(body)
    }
    return fetch(`/api/internal/${api}`, options).then((response) => {
        if (response.ok) {
            return contentType ? response.blob() : response.json()
        }
        return response
    })
}
