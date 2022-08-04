import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ViewPanel } from './ViewPanel';

function eventHandlers() {
    return {
        setHiddenColumns: jest.fn(),
        setVisibleDetailsTabs: jest.fn(),
        handleSort: jest.fn(),
        setDateInterval: jest.fn(),
        setDateOrder: jest.fn(),
        setHideMetricsNotRequiringAction: jest.fn(),
        setNrDates: jest.fn(),
        setShowIssueCreationDate: jest.fn(),
        setShowIssueSummary: jest.fn(),
        setShowIssueUpdateDate: jest.fn(),
        setShowIssueDueDate: jest.fn(),
        setShowIssueRelease: jest.fn(),
        setShowIssueSprint: jest.fn(),
        setUIMode: jest.fn()
    }
}

it('resets the settings', () => {
    const props = eventHandlers();
    render(
        <ViewPanel
            dateInterval={14}
            dateOrder="ascending"
            hiddenColumns={["trend"]}
            hideMetricsNotRequiringAction={true}
            issueSettings={
                {
                    showIssueCreationDate: true,
                    showIssueSummary: true,
                    showIssueUpdateDate: true,
                    showIssueDueDate: true,
                    showIssueRelease: true,
                    showIssueSprint: true
                }
            }
            nrDates={7}
            sortColumn="status"
            sortDirection="descending"
            uiMode="dark"
            visibleDetailsTabs={["tab"]}
            {...props}
        />
    )
    fireEvent.click(screen.getByText(/Reset all settings/))
    expect(props.setVisibleDetailsTabs).toHaveBeenCalledWith([])
    expect(props.setHiddenColumns).toHaveBeenCalledWith([])
    expect(props.handleSort).toHaveBeenCalled()
    expect(props.setDateInterval).toHaveBeenCalled()
    expect(props.setDateOrder).toHaveBeenCalled()
    expect(props.setNrDates).toHaveBeenCalled()
    expect(props.setHideMetricsNotRequiringAction).toHaveBeenCalled()
    expect(props.setShowIssueCreationDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueSummary).toHaveBeenCalledWith(false)
    expect(props.setShowIssueUpdateDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueDueDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueRelease).toHaveBeenCalledWith(false)
    expect(props.setShowIssueSprint).toHaveBeenCalledWith(false)
    expect(props.setUIMode).toHaveBeenCalledWith(null)
})

it('does not reset the settings when all have the default value', () => {
    const props = eventHandlers();
    render(
        <ViewPanel
            dateInterval={7}
            dateOrder="descending"
            hiddenColumns={[]}
            hideMetricsNotRequiringAction={false}
            issueSettings={
                {
                    showIssueCreationDate: false,
                    showIssueSummary: false,
                    showIssueUpdateDate: false,
                    showIssueDueDate: false,
                    showIssueRelease: false,
                    showIssueSprint: false
                }
            }
            nrDates={1}
            sortColumn={null}
            sortDirection="ascending"
            uiMode={null}
            visibleDetailsTabs={[]}
            {...props}
        />
    )
    fireEvent.click(screen.getByText(/Reset all settings/))
    expect(props.setVisibleDetailsTabs).not.toHaveBeenCalled()
    expect(props.setHiddenColumns).not.toHaveBeenCalled()
    expect(props.handleSort).not.toHaveBeenCalled()
    expect(props.setDateInterval).not.toHaveBeenCalled()
    expect(props.setDateOrder).not.toHaveBeenCalled()
    expect(props.setNrDates).not.toHaveBeenCalled()
    expect(props.setHideMetricsNotRequiringAction).not.toHaveBeenCalled()
    expect(props.setShowIssueCreationDate).not.toHaveBeenCalled()
    expect(props.setShowIssueSummary).not.toHaveBeenCalled()
    expect(props.setShowIssueUpdateDate).not.toHaveBeenCalled()
    expect(props.setShowIssueDueDate).not.toHaveBeenCalled()
    expect(props.setShowIssueRelease).not.toHaveBeenCalled()
    expect(props.setShowIssueSprint).not.toHaveBeenCalled()
    expect(props.setUIMode).not.toHaveBeenCalled()
})

it("sets dark mode", () => {
    const setUIMode = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={false} setUIMode={setUIMode} />)
    fireEvent.click(screen.getByText(/Dark mode/))
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("sets light mode", () => {
    const setUIMode = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={false} setUIMode={setUIMode} uiMode="dark" />)
    fireEvent.click(screen.getByText(/Light mode/))
    expect(setUIMode).toHaveBeenCalledWith("light")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={true} setUIMode={setUIMode} />)
    await userEvent.type(screen.getByText(/Dark mode/), "{Enter}")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("hides the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={false} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/Metrics requiring action/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(true)
})

it("shows the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/All metrics/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("shows the metrics not requiring action by keypress", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    await userEvent.type(screen.getByText(/All metrics/), "{Enter}")
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("hides a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getByText(/Trend/))
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
    await userEvent.type(screen.getAllByText(/Comment/)[0], "{Enter}")
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(toggleHiddenColumn).toHaveBeenCalledWith("status")
})

it("sorts a column", () => {
    const handleSort = jest.fn();
    render(<ViewPanel handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column descending", () => {
    const handleSort = jest.fn();
    render(<ViewPanel sortColumn="comment" sortDirection="ascending" handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    render(<ViewPanel handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    const handleSort = jest.fn();
    render(<ViewPanel hiddenColumns={["comment"]} handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    expect(handleSort).not.toHaveBeenCalledWith("comment")
})

it("sets the number of dates", () => {
    const setNrDates = jest.fn();
    render(<ViewPanel nrDates={2} setNrDates={setNrDates} />)
    fireEvent.click(screen.getByText(/7 dates/))
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("sets the number of dates by keypress", async () => {
    const setNrDates = jest.fn();
    render(<ViewPanel nrDates={1} setNrDates={setNrDates} />)
    await userEvent.type(screen.getByText(/5 dates/), "{Enter}")
    expect(setNrDates).toHaveBeenCalledWith(5)
})

it("sets the date interval to weeks", () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel dateInterval={1} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/2 weeks/))
    expect(setDateInterval).toHaveBeenCalledWith(14)
})

it("sets the date interval to one day", () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel dateInterval={7} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/1 day/))
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sets the date interval by keypress", async () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel dateInterval={7} setDateInterval={setDateInterval} />)
    await userEvent.type(screen.getByText(/1 day/), "{Enter}")
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sorts the dates descending", () => {
    const setDateOrder = jest.fn();
    render(<ViewPanel dateOrder="ascending" setDateOrder={setDateOrder} />)
    fireEvent.click(screen.getByText(/Descending/))
    expect(setDateOrder).toHaveBeenCalledWith("descending")
})

it("sorts the dates ascending by keypress", async () => {
    const setDateOrder = jest.fn();
    render(<ViewPanel dateOrder="descending" setDateOrder={setDateOrder} />)
    await userEvent.type(screen.getByText(/Ascending/), "{Enter}")
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})

it("shows issue summaries", async () => {
    const setShowIssueSummary = jest.fn();
    render(<ViewPanel setShowIssueSummary={setShowIssueSummary} />)
    await act(async () => { fireEvent.click(screen.getAllByText(/Summary/)[0]) });
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})

it("shows issue summaries by keypress", async () => {
    const setShowIssueSummary = jest.fn();
    render(<ViewPanel setShowIssueSummary={setShowIssueSummary} />)
    await userEvent.type(screen.getAllByText(/Summary/)[0], "{Enter}")
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})
