import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ViewPanel } from './ViewPanel';

it("clears the visible details tabs", async () => {
    const clearVisibleDetailsTabs = jest.fn();
    await act(async () => {
        render(<ViewPanel clearVisibleDetailsTabs={clearVisibleDetailsTabs} visibleDetailsTabs={["tab"]} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(clearVisibleDetailsTabs).toHaveBeenCalled()
})

it("doesn't clear the visible details tabs if there are none", async () => {
    const clearVisibleDetailsTabs = jest.fn();
    await act(async () => {
        render(<ViewPanel clearVisibleDetailsTabs={clearVisibleDetailsTabs} visibleDetailsTabs={[]} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(clearVisibleDetailsTabs).not.toHaveBeenCalled()
})

function eventHandlers() {
    return {
        clearHiddenColumns: jest.fn(),
        clearVisibleDetailsTabs: jest.fn(),
        setDateInterval: jest.fn(),
        setDateOrder: jest.fn(),
        setHideMetricsNotRequiringAction: jest.fn(),
        setNrDates: jest.fn(),
        setShowIssueCreationDate: jest.fn(),
        setShowIssueSummary: jest.fn(),
        setShowIssueUpdateDate: jest.fn(),
        setSortColumn: jest.fn(),
        setSortDirection: jest.fn(),
        setUIMode: jest.fn()
    }
}

it('resets the settings', async () => {
    const props = eventHandlers();
    await act(async () => {
        render(
            <ViewPanel
                dateInterval={14}
                dateOrder="ascending"
                hiddenColumns={["trend"]}
                hideMetricsNotRequiringAction={true}
                nrDates={7}
                showIssueCreationDate={true}
                showIssueSummary={true}
                showIssueUpdateDate={true}
                sortColumn="status"
                sortDirection="descending"
                uiMode="dark"
                visibleDetailsTabs={["tab"]}
                {...props}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(props.clearVisibleDetailsTabs).toHaveBeenCalled()
    expect(props.clearHiddenColumns).toHaveBeenCalled()
    expect(props.setDateInterval).toHaveBeenCalled()
    expect(props.setDateOrder).toHaveBeenCalled()
    expect(props.setNrDates).toHaveBeenCalled()
    expect(props.setHideMetricsNotRequiringAction).toHaveBeenCalled()
    expect(props.setShowIssueCreationDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueSummary).toHaveBeenCalledWith(false)
    expect(props.setShowIssueUpdateDate).toHaveBeenCalledWith(false)
    expect(props.setSortColumn).toHaveBeenCalledWith(null)
    expect(props.setSortDirection).toHaveBeenCalledWith("ascending")
    expect(props.setUIMode).toHaveBeenCalledWith(null)
})

it('does not reset the settings when all have the default value', async () => {
    const props = eventHandlers();
    await act(async () => {
        render(
            <ViewPanel
                dateInterval={7}
                dateOrder="descending"
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={false}
                nrDates={1}
                showIssueCreationDate={false}
                showIssueSummary={false}
                showIssueUpdateDate={false}
                sortColumn={null}
                sortDirection="ascending"
                uiMode={null}
                visibleDetailsTabs={[]}
                {...props}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(props.clearVisibleDetailsTabs).not.toHaveBeenCalled()
    expect(props.clearHiddenColumns).not.toHaveBeenCalled()
    expect(props.setDateInterval).not.toHaveBeenCalled()
    expect(props.setDateOrder).not.toHaveBeenCalled()
    expect(props.setNrDates).not.toHaveBeenCalled()
    expect(props.setHideMetricsNotRequiringAction).not.toHaveBeenCalled()
    expect(props.setShowIssueCreationDate).not.toHaveBeenCalled()
    expect(props.setShowIssueSummary).not.toHaveBeenCalled()
    expect(props.setShowIssueUpdateDate).not.toHaveBeenCalled()
    expect(props.setSortColumn).not.toHaveBeenCalled()
    expect(props.setSortDirection).not.toHaveBeenCalled()
    expect(props.setUIMode).not.toHaveBeenCalled()
})

it("sets dark mode", async () => {
    const setUIMode = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={false} setUIMode={setUIMode} />)
        fireEvent.click(screen.getByText(/Dark mode/))
    });
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("sets light mode", async () => {
    const setUIMode = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={false} setUIMode={setUIMode} uiMode="dark" />)
        fireEvent.click(screen.getByText(/Light mode/))
    });
    expect(setUIMode).toHaveBeenCalledWith("light")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={true} setUIMode={setUIMode} />)
        await userEvent.type(screen.getByText(/Dark mode/), "{Enter}")
    });
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("hides the metrics not requiring action", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={false} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
        fireEvent.click(screen.getByText(/Metrics requiring action/))
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(true)
})

it("shows the metrics not requiring action", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
        fireEvent.click(screen.getByText(/All metrics/))
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("shows the metrics not requiring action by keypress", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(<ViewPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
        await userEvent.type(screen.getByText(/All metrics/), "{Enter}")
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("hides a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
        fireEvent.click(screen.getByText(/Trend/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
        await userEvent.type(screen.getAllByText(/Comment/)[0], "{Enter}")
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
        fireEvent.click(screen.getAllByText(/Status/)[0])
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("status")
})

it("sorts a column", async () => {
    const setSortColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel setSortColumn={setSortColumn} />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(setSortColumn).toHaveBeenCalledWith("comment")
})

it("unsorts a column", async () => {
    const setSortColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel setSortColumn={setSortColumn} sortColumn="comment" />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(setSortColumn).toHaveBeenCalledWith(null)
})

it("sorts a column by keypress", async () => {
    const setSortColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel setSortColumn={setSortColumn} />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(setSortColumn).toHaveBeenCalledWith("comment")
})

it("unsorts a column by keypress", async () => {
    const setSortColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel setSortColumn={setSortColumn} sortColumn="comment" />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(setSortColumn).toHaveBeenCalledWith(null)
})

it("sets the number of dates", async () => {
    const setNrDates = jest.fn();
    await act(async () => {
        render(<ViewPanel nrDates={2} setNrDates={setNrDates} />)
        fireEvent.click(screen.getByText(/7 dates/))
    });
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("sets the number of dates by keypress", async () => {
    const setNrDates = jest.fn();
    await act(async () => {
        render(<ViewPanel nrDates={1} setNrDates={setNrDates} />)
        await userEvent.type(screen.getByText(/5 dates/), "{Enter}")
    });
    expect(setNrDates).toHaveBeenCalledWith(5)
})

it("sets the date interval to weeks", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(<ViewPanel dateInterval={1} setDateInterval={setDateInterval} />)
        fireEvent.click(screen.getByText(/2 weeks/))
    });
    expect(setDateInterval).toHaveBeenCalledWith(14)
})

it("sets the date interval to one day", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(<ViewPanel dateInterval={7} setDateInterval={setDateInterval} />)
        fireEvent.click(screen.getByText(/1 day/))
    });
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sets the date interval by keypress", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(<ViewPanel dateInterval={7} setDateInterval={setDateInterval} />)
        await userEvent.type(screen.getByText(/1 day/), "{Enter}")
    });
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sorts the dates descending", async () => {
    const setDateOrder = jest.fn();
    await act(async () => {
        render(<ViewPanel dateOrder="ascending" setDateOrder={setDateOrder} />)
        fireEvent.click(screen.getAllByText(/Descending/)[1])
    });
    expect(setDateOrder).toHaveBeenCalledWith("descending")
})

it("sorts the dates ascending by keypress", async () => {
    const setDateOrder = jest.fn();
    await act(async () => {
        render(<ViewPanel dateOrder="descending" setDateOrder={setDateOrder} />)
        await userEvent.type(screen.getAllByText(/Ascending/)[1], "{Enter}")
    });
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})

it("shows issue summaries", async () => {
    const setShowIssueSummary = jest.fn();
    await act(async () => {
        render(<ViewPanel setShowIssueSummary={setShowIssueSummary} />)
        fireEvent.click(screen.getAllByText(/Summary/)[0])
    });
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})

it("shows issue summaries by keypress", async () => {
    const setShowIssueSummary = jest.fn();
    await act(async () => {
        render(<ViewPanel setShowIssueSummary={setShowIssueSummary} />)
        await userEvent.type(screen.getAllByText(/Summary/)[0], "{Enter}")
    });
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})
