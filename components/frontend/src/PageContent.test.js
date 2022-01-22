import React from 'react';
import { render, screen } from '@testing-library/react';
import { PageContent } from './PageContent';

it('shows the reports overview', () =>{
    render(<PageContent reports={[]} />)
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('shows the report', () => {
    render(<PageContent history={{location: {}}} reports={[{}]} report_uuid="uuid" />)
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
})

it('shows the loading spinner', () =>{
    render(<PageContent loading />)
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})
