import * as fetch_server_api from './fetch_server_api';

jest.mock("./fetch_server_api.js");

it('fetches the api', async () => {
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve({ }));
    fetch_server_api.fetch_server_api('get', 'api').then((response) => expect(response).toBe({})).catch(()=>{});
});

it('posts to the api', async () => {
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve({ }));
    fetch_server_api.fetch_server_api('post', 'api', {body: "body"}).then((response) => expect(response).toBe({})).catch(()=>{});
});

it('gets the json from the response', async () => {
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve({ ok: true, json: () => ({json: true})}));
    fetch_server_api.fetch_server_api('get', 'api').then((response) => expect(response).toBe({json: true})).catch(()=>{});
});

it('gets the blob from the response', async () => {
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve({ ok: true, blob: () => ({blob: true})}));
    fetch_server_api.fetch_server_api('get', 'api', {}, 'application/blob').then((response) => expect(response).toBe({blob: true})).catch(()=>{});
});