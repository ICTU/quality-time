import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { put_settings } from '../api/settings';
import { DEFAULT_SETTINGS } from '../utils';
import { ViewPanel } from './ViewPanel';

jest.mock('../api/settings')

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
            defaultSettings={DEFAULT_SETTINGS}
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
            defaultSettings={DEFAULT_SETTINGS}
            dateInterval={DEFAULT_SETTINGS.date_interval}
            dateOrder={DEFAULT_SETTINGS.date_order}
            hiddenColumns={DEFAULT_SETTINGS.hidden_columns}
            hideMetricsNotRequiringAction={DEFAULT_SETTINGS.hide_metrics_not_requiring_action}
            issueSettings={
                {
                    showIssueCreationDate: DEFAULT_SETTINGS.show_issue_creation_date,
                    showIssueSummary: DEFAULT_SETTINGS.show_issue_summary,
                    showIssueUpdateDate: DEFAULT_SETTINGS.show_issue_update_date,
                    showIssueDueDate: DEFAULT_SETTINGS.show_issue_due_date,
                    showIssueRelease: DEFAULT_SETTINGS.show_issue_release,
                    showIssueSprint: DEFAULT_SETTINGS.show_issue_sprint
                }
            }
            nrDates={DEFAULT_SETTINGS.nr_dates}
            sortColumn={DEFAULT_SETTINGS.sort_column}
            sortDirection={DEFAULT_SETTINGS.sort_direction}
            uiMode={DEFAULT_SETTINGS.ui_mode}
            visibleDetailsTabs={DEFAULT_SETTINGS.tabs}
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

it('saves the settings', async () => {
    const props = eventHandlers();
    await act(async () => {
        render(
            <ViewPanel
                setDefaultSettings={jest.fn()}
                defaultSettings={DEFAULT_SETTINGS}
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
        fireEvent.click(screen.getByText(/Save settings/))
    });
    expect(put_settings).toHaveBeenCalledWith({
        "date_interval": 14,
        "date_order": "ascending",
        "hidden_columns": ["trend"],
        "hide_metrics_not_requiring_action": true,
        "nr_dates": 7, "show_issue_creation_date": true,
        "show_issue_due_date": true,
        "show_issue_release": true,
        "show_issue_sprint": true,
        "show_issue_summary": true,
        "show_issue_update_date": true,
        "sort_column": "status",
        "sort_direction": "descending",
        "tabs": ["tab"],
        "ui_mode": "dark"
    })
})

it('does not save the settings when all have the default value', async () => {
    const props = eventHandlers();
    await act(async () => {
        render(
            <ViewPanel
                defaultSettings={DEFAULT_SETTINGS}
                dateInterval={DEFAULT_SETTINGS.date_interval}
                dateOrder={DEFAULT_SETTINGS.date_order}
                hiddenColumns={DEFAULT_SETTINGS.hidden_columns}
                hideMetricsNotRequiringAction={DEFAULT_SETTINGS.hide_metrics_not_requiring_action}
                issueSettings={
                    {
                        showIssueCreationDate: DEFAULT_SETTINGS.show_issue_creation_date,
                        showIssueSummary: DEFAULT_SETTINGS.show_issue_summary,
                        showIssueUpdateDate: DEFAULT_SETTINGS.show_issue_update_date,
                        showIssueDueDate: DEFAULT_SETTINGS.show_issue_due_date,
                        showIssueRelease: DEFAULT_SETTINGS.show_issue_release,
                        showIssueSprint: DEFAULT_SETTINGS.show_issue_sprint
                    }
                }
                nrDates={DEFAULT_SETTINGS.nr_dates}
                sortColumn={DEFAULT_SETTINGS.sort_column}
                sortDirection={DEFAULT_SETTINGS.sort_direction}
                uiMode={DEFAULT_SETTINGS.ui_mode}
                visibleDetailsTabs={DEFAULT_SETTINGS.tabs}
                {...props}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(put_settings).not.toHaveBeenCalledWith()
})

it("sets dark mode", async () => {
    const setUIMode = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={false} setUIMode={setUIMode} />)
    fireEvent.click(screen.getByText(/Dark mode/))
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("sets light mode", () => {
    const setUIMode = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={false} setUIMode={setUIMode} uiMode="dark" />)
    fireEvent.click(screen.getByText(/Light mode/))
    expect(setUIMode).toHaveBeenCalledWith("light")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={true} setUIMode={setUIMode} />)
    await userEvent.type(screen.getByText(/Dark mode/), "{Enter}")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("hides the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={false} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/Metrics requiring action/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(true)
})

it("shows the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/All metrics/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("shows the metrics not requiring action by keypress", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    await userEvent.type(screen.getByText(/All metrics/), "{Enter}")
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("hides a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getByText(/Trend/))
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} toggleHiddenColumn={toggleHiddenColumn} />)
    await userEvent.type(screen.getAllByText(/Comment/)[0], "{Enter}")
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(toggleHiddenColumn).toHaveBeenCalledWith("status")
})

it("sorts a column", () => {
    const handleSort = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column descending", () => {
    const handleSort = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} sortColumn="comment" sortDirection="ascending" handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    const handleSort = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} hiddenColumns={["comment"]} handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    expect(handleSort).not.toHaveBeenCalledWith("comment")
})

it("sets the number of dates", () => {
    const setNrDates = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} nrDates={2} setNrDates={setNrDates} />)
    fireEvent.click(screen.getByText(/7 dates/))
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("sets the number of dates by keypress", async () => {
    const setNrDates = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} nrDates={1} setNrDates={setNrDates} />)
    await userEvent.type(screen.getByText(/5 dates/), "{Enter}")
    expect(setNrDates).toHaveBeenCalledWith(5)
})

it("sets the date interval to weeks", () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} dateInterval={1} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/2 weeks/))
    expect(setDateInterval).toHaveBeenCalledWith(14)
})

it("sets the date interval to one day", () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} dateInterval={7} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/1 day/))
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sets the date interval by keypress", async () => {
    const setDateInterval = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} dateInterval={7} setDateInterval={setDateInterval} />)
    await userEvent.type(screen.getByText(/1 day/), "{Enter}")
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sorts the dates descending", () => {
    const setDateOrder = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} dateOrder="ascending" setDateOrder={setDateOrder} />)
    fireEvent.click(screen.getByText(/Descending/))
    expect(setDateOrder).toHaveBeenCalledWith("descending")
})

it("sorts the dates ascending by keypress", async () => {
    const setDateOrder = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} dateOrder="descending" setDateOrder={setDateOrder} />)
    await userEvent.type(screen.getByText(/Ascending/), "{Enter}")
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})

it("shows issue summaries", async () => {
    const setShowIssueSummary = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} setShowIssueSummary={setShowIssueSummary} />)
    fireEvent.click(screen.getAllByText(/Summary/)[0])
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})

it("shows issue summaries by keypress", async () => {
    const setShowIssueSummary = jest.fn();
    render(<ViewPanel defaultSettings={DEFAULT_SETTINGS} setShowIssueSummary={setShowIssueSummary} />)
    await userEvent.type(screen.getAllByText(/Summary/)[0], "{Enter}")
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})
