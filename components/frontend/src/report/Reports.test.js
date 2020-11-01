import React from 'react';
import { render, screen } from '@testing-library/react';
import { Reports } from './Reports';

it('shows an error message if there are no reports at the specified date', () => {
  render(<Reports reports={[]} report_date="today" />);
  expect(screen.getAllByText(/Sorry, no reports existed at today/).length).toBe(1);
});

it('shows the report overview', () => {
  render(
    <Reports
      reports={[{summary: {red: 0, green: 0, yellow: 0, grey: 0, white: 0}, summary_by_tag: {}}]}
      reports_overview={{title: "Overview"}}
    />
  );
  expect(screen.getAllByText(/Overview/).length).toBe(1);
});