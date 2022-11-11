import React from 'react';
import { act, render } from '@testing-library/react';
import { ChangeLog } from './ChangeLog';
import * as changelog_api from '../api/changelog';

jest.mock("../api/changelog.js");

it('renders no changes', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));
    let result;
    await act(async () => {result = render(<ChangeLog />);})
    const rows = result.container.querySelectorAll('div.event');
    expect(rows.length).toBe(0);
});

it('renders one report change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    let result;
    await act(async () => {result = render(<ChangeLog report_uuid="uuid" />);})
    const rows = result.container.querySelectorAll('div.event');
    expect(rows.length).toBe(1);
});

it('renders one subject change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    let result;
    await act(async () => { result = render(<ChangeLog subject_uuid="uuid" />) });
    const rows = result.container.querySelectorAll('div.event');
    expect(rows.length).toBe(1);
});

it('renders one metric change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    let result;
    await act(async () => { result = render(<ChangeLog metric_uuid="uuid" />) });
    const rows = result.container.querySelectorAll('div.event');
    expect(rows.length).toBe(1);
});

it('renders one source change', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{timestamp: "2020-01-01"}] }));
    let result;
    await act(async () => { result = render(<ChangeLog source_uuid="uuid" />) });
    const rows = result.container.querySelectorAll('div.event');
    expect(rows.length).toBe(1);
});
