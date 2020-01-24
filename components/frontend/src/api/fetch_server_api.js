export const api_version = 'v2'

export function fetch_server_api(method, api, body, content_type) {
  let options = {
    method: method,
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': content_type || 'application/json'
    }
  }
  if (method === 'post') {
    options['body'] = JSON.stringify(body)
  }
  return fetch(`/api/${api_version}/${api}`, options).then(
    (response) => { return response.ok ? (content_type ? response.blob() : response.json()) : response })
}
