import React from 'react';
import { render, screen } from '@testing-library/react';
import { PageContent } from './PageContent';

it('shows the reports overview', () =>{
    render(<PageContent reports={[]} />)
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('shows that the report is missing', () => {
    render(<PageContent history={{location: {}}} reports={[{}]} report_uuid="uuid" />)
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
})

it('shows that the report was missing', () => {
    render(<PageContent dateOrder="ascending" history={{location: {}}} report_date="2022-03-31" reports={[{}]} report_uuid="uuid" />)
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
})

it('shows the loading spinner', () =>{
    render(<PageContent loading />)
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})
