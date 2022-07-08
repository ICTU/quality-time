import React from 'react';
import { render, screen } from '@testing-library/react';
import { PageContent } from './PageContent';

let settings_fixture = {
    date_interval: 7,
    date_order: "descending",
    hidden_columns: [],
    hide_metrics_not_requiring_action: false,
    nr_dates: 1,
    sort_column: null,
    sort_direction: "ascending",
    tabs: [],
    show_issue_summary: false,
    show_issue_creation_date: false,
    show_issue_update_date: false,
    ui_mode: null
}

it('shows the reports overview', () =>{
    render(<PageContent reports={[]} settings={settings_fixture} />)
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('shows that the report is missing', () => {
    render(<PageContent history={{location: {}}} reports={[{}]} report_uuid="uuid" settings={settings_fixture} />)
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
})

it('shows that the report was missing', () => {
    render(<PageContent dateOrder="ascending" history={{location: {}}} report_date="2022-03-31" reports={[{}]} report_uuid="uuid" settings={settings_fixture} />)
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
})

it('shows the loading spinner', () =>{
    render(<PageContent loading settings={settings_fixture} />)
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})
