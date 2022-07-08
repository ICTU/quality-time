import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ViewPanel } from './ViewPanel';

let settingsFixture = {
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

it("clears the visible details tabs", async () => {
    const  postSettings = jest.fn();
    const settings = {...settingsFixture, tabs: ["tab"]}
    await act(async () => {
        render(<ViewPanel postSettings={postSettings} settings={settings} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(postSettings).toHaveBeenCalled()
})

it("doesn't clear the visible details tabs if there are none", async () => {
    const postSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel postSettings={postSettings} visibleDetailsTabs={[]} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(postSettings).not.toHaveBeenCalled()
})

function eventHandlers() {
    return {
        clearHiddenColumns: jest.fn(),
        clearVisibleDetailsTabs: jest.fn(),
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

it('resets the settings', async () => {
    const props = eventHandlers();
    await act(async () => {
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
    });
    expect(props.clearVisibleDetailsTabs).toHaveBeenCalled()
    expect(props.clearHiddenColumns).toHaveBeenCalled()
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

it('does not reset the settings when all have the default value', async () => {
    const props = eventHandlers();
    await act(async () => {
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
    });
    expect(props.clearVisibleDetailsTabs).not.toHaveBeenCalled()
    expect(props.clearHiddenColumns).not.toHaveBeenCalled()
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
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel handleSort={handleSort} />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column descending", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel sortColumn="comment" sortDirection="ascending" handleSort={handleSort} />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel handleSort={handleSort} />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel hiddenColumns={["comment"]} handleSort={handleSort} />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(handleSort).not.toHaveBeenCalledWith("comment")
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
    const setSettings = jest.fn();
    const settings = {...settingsFixture, date_order: "ascending"}
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settings} />)
        fireEvent.click(screen.getByText(/Descending/))
    });
    expect(setSettings).toHaveBeenCalledWith({"date_order": "descending"})
})

it("sorts the dates ascending by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/Ascending/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"date_order": "ascending"})
})

it("shows issue summaries", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getAllByText(/Summary/)[0])
    });
    expect(setSettings).toHaveBeenCalledWith({"show_issue_summary": true})
})

it("shows issue summaries by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getAllByText(/Summary/)[0], "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"show_issue_summary": true})
})
