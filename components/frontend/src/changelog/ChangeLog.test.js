import React from 'react';
import ReactDOM from 'react-dom';
import { act } from 'react-dom/test-utils';
import { ChangeLog } from './ChangeLog';
import * as changelog_api from '../api/changelog';

jest.mock("../api/changelog.js");
let container;

beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
});

afterEach(() => {
    document.body.removeChild(container);
    container = null;
});

it('renders no changes', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));
    await act(async () => { ReactDOM.render(<ChangeLog />, container) });
    const rows = container.querySelectorAll('tr');
    expect(rows.length).toBe(2);
});

it('renders one report change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    await act(async () => { ReactDOM.render(<ChangeLog report_uuid="uuid" />, container) });
    const rows = container.querySelectorAll('tr');
    expect(rows.length).toBe(3);
});

it('renders one subject change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    await act(async () => { ReactDOM.render(<ChangeLog subject_uuid="uuid" />, container) });
    const rows = container.querySelectorAll('tr');
    expect(rows.length).toBe(3);
});

it('renders one metric change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    await act(async () => { ReactDOM.render(<ChangeLog metric_uuid="uuid" />, container) });
    const rows = container.querySelectorAll('tr');
    expect(rows.length).toBe(3);
});

it('renders one source change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    await act(async () => { ReactDOM.render(<ChangeLog source_uuid="uuid" />, container) });
    const rows = container.querySelectorAll('tr');
    expect(rows.length).toBe(3);
});
