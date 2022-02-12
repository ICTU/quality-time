import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import { datamodel, report } from "./__fixtures__/fixtures";
import { AppUI } from './AppUI';

it('shows an error message when there are no reports', () =>{
    render(<AppUI history={{location: {search: ""}}} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('handles sorting', async () => {
    const history = createMemoryHistory()
    render(<AppUI datamodel={datamodel} history={history} report_date={null} report_uuid="report_uuid" reports={[report]} reports_overview={{}} user="xxx" />)
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column=comment")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column=status")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column=status&sort_direction=descending")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("")
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column=comment")
    await act(async () => fireEvent.click(screen.getAllByText(/Add metric/)[0]))
    expect(history.location.search).toEqual("")
})
