export function fetch_server_api(method, api, body) {
  let options = {
    method: method,
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  }
  if (method === 'post') {
    options['body'] = JSON.stringify(body)
  }
  return fetch(`/api/v1/${api}`, options).then((response) => response.json());
}
