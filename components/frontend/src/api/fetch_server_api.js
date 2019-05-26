export function fetch_server_api(method, api, body, success) {
  fetch(`${window.server_url}/${api}`, {
    method: method,
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  }).then(() => success());
}
