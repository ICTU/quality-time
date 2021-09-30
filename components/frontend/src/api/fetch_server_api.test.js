import { fetch_server_api } from './fetch_server_api';

it('fetches the api', async () => {
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({}));
    fetch_server_api('get', 'api').then((response) => expect(response).toBe({})).catch(() => {/*Prevent unhandled promise*/ });
});

it('posts to the api', async () => {
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({}));
    fetch_server_api('post', 'api', { body: "body" }).then((response) => expect(response).toBe({})).catch(() => {/*Prevent unhandled promise*/ });
});

it('gets the json from the response', async () => {
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({ ok: true, json: () => ({ json: true }) }));
    fetch_server_api('get', 'api').then((response) => expect(response).toBe({ json: true })).catch(() => {/*Prevent unhandled promise*/ });
});

it('gets the blob from the response', async () => {
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({ ok: true, blob: () => ({ blob: true }) }));
    fetch_server_api('get', 'api', {}, 'application/blob').then((response) => expect(response).toBe({ blob: true })).catch(() => {/*Prevent unhandled promise*/ });
});