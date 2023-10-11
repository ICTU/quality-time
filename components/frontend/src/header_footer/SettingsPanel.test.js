import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SettingsPanel } from './SettingsPanel';

function eventHandlers() {
    return {
        clearHiddenColumns: jest.fn(),
        clearHiddenTags: jest.fn(),
        clearVisibleDetailsTabs: jest.fn(),
        handleDateChange: jest.fn(),
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
    }
}

it('resets the settings', () => {
    const props = eventHandlers();
    render(
        <SettingsPanel
            dateInterval={14}
            dateOrder="ascending"
            hiddenColumns={["trend"]}
            hiddenTags={["security"]}
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
            reportDate={new Date("2023-01-01")}
            sortColumn="status"
            sortDirection="descending"
            visibleDetailsTabs={["tab"]}
            {...props}
        />
    )
    fireEvent.click(screen.getByText(/Reset all settings/))
    expect(props.clearHiddenColumns).toHaveBeenCalledWith()
    expect(props.clearHiddenTags).toHaveBeenCalledWith()
    expect(props.clearVisibleDetailsTabs).toHaveBeenCalledWith()
    expect(props.handleDateChange).toHaveBeenCalledWith(null)
    expect(props.handleSort).toHaveBeenCalledWith(null)
    expect(props.setDateInterval).toHaveBeenCalledWith(7)
    expect(props.setDateOrder).toHaveBeenCalledWith("descending")
    expect(props.setNrDates).toHaveBeenCalledWith(1)
    expect(props.setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
    expect(props.setShowIssueCreationDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueSummary).toHaveBeenCalledWith(false)
    expect(props.setShowIssueUpdateDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueDueDate).toHaveBeenCalledWith(false)
    expect(props.setShowIssueRelease).toHaveBeenCalledWith(false)
    expect(props.setShowIssueSprint).toHaveBeenCalledWith(false)
})

it('does not reset the settings when all have the default value', () => {
    const props = eventHandlers();
    render(
        <SettingsPanel
            dateInterval={7}
            dateOrder="descending"
            hiddenColumns={[]}
            hiddenTags={[]}
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
            reportDate={null}
            sortColumn={null}
            sortDirection="ascending"
            visibleDetailsTabs={[]}
            {...props}
        />
    )
    fireEvent.click(screen.getByText(/Reset all settings/))
    expect(props.clearHiddenColumns).not.toHaveBeenCalled()
    expect(props.clearHiddenTags).not.toHaveBeenCalled()
    expect(props.clearVisibleDetailsTabs).not.toHaveBeenCalled()
    expect(props.handleDateChange).not.toHaveBeenCalled()
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
})

it("hides the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<SettingsPanel hideMetricsNotRequiringAction={false} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/Metrics requiring action/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(true)
})

it("shows the metrics not requiring action", () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<SettingsPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    fireEvent.click(screen.getByText(/All metrics/))
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("shows the metrics not requiring action by keypress", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    render(<SettingsPanel hideMetricsNotRequiringAction={true} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />)
    await userEvent.type(screen.getByText(/All metrics/), " ")
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("hides a tag", () => {
    const toggleHiddenTag = jest.fn();
    render(<SettingsPanel tags={["security"]} toggleHiddenTag={toggleHiddenTag} />)
    fireEvent.click(screen.getByText(/security/))
    expect(toggleHiddenTag).toHaveBeenCalledWith("security")
})

it("hides a tag by keypress", async () => {
    const toggleHiddenTag = jest.fn();
    render(<SettingsPanel tags={["security"]} toggleHiddenTag={toggleHiddenTag} />)
    await userEvent.type(screen.getAllByText(/security/)[0], " ")
    expect(toggleHiddenTag).toHaveBeenCalledWith("security")
})

it("shows a tag", () => {
    const toggleHiddenTag = jest.fn();
    render(<SettingsPanel tags={["security"]} hiddenTags={["security"]} toggleHiddenTag={toggleHiddenTag} />)
    fireEvent.click(screen.getAllByText(/security/)[0])
    expect(toggleHiddenTag).toHaveBeenCalledWith("security")
})

it("hides a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<SettingsPanel toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getByText(/Trend/))
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    render(<SettingsPanel toggleHiddenColumn={toggleHiddenColumn} />)
    await userEvent.type(screen.getAllByText(/Comment/)[0], " ")
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", () => {
    const toggleHiddenColumn = jest.fn();
    render(<SettingsPanel toggleHiddenColumn={toggleHiddenColumn} />)
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(toggleHiddenColumn).toHaveBeenCalledWith("status")
})

it("sorts a column", () => {
    const handleSort = jest.fn();
    render(<SettingsPanel handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column descending", () => {
    const handleSort = jest.fn();
    render(<SettingsPanel sortColumn="comment" sortDirection="ascending" handleSort={handleSort} />)
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    render(<SettingsPanel handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    const handleSort = jest.fn();
    render(<SettingsPanel hiddenColumns={["comment"]} handleSort={handleSort} />)
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).not.toHaveBeenCalledWith("comment")
})

it("sets the number of dates", () => {
    const setNrDates = jest.fn();
    render(<SettingsPanel nrDates={2} setNrDates={setNrDates} />)
    fireEvent.click(screen.getByText(/7 dates/))
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("sets the number of dates by keypress", async () => {
    const setNrDates = jest.fn();
    render(<SettingsPanel nrDates={1} setNrDates={setNrDates} />)
    await userEvent.type(screen.getByText(/5 dates/), " ")
    expect(setNrDates).toHaveBeenCalledWith(5)
})

it("sets the date interval to weeks", () => {
    const setDateInterval = jest.fn();
    render(<SettingsPanel dateInterval={1} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/2 weeks/))
    expect(setDateInterval).toHaveBeenCalledWith(14)
})

it("sets the date interval to one day", () => {
    const setDateInterval = jest.fn();
    render(<SettingsPanel dateInterval={7} setDateInterval={setDateInterval} />)
    fireEvent.click(screen.getByText(/1 day/))
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sets the date interval by keypress", async () => {
    const setDateInterval = jest.fn();
    render(<SettingsPanel dateInterval={7} setDateInterval={setDateInterval} />)
    await userEvent.type(screen.getByText(/1 day/), " ")
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sorts the dates descending", () => {
    const setDateOrder = jest.fn();
    render(<SettingsPanel dateOrder="ascending" setDateOrder={setDateOrder} />)
    fireEvent.click(screen.getByText(/Descending/))
    expect(setDateOrder).toHaveBeenCalledWith("descending")
})

it("sorts the dates ascending by keypress", async () => {
    const setDateOrder = jest.fn();
    render(<SettingsPanel dateOrder="descending" setDateOrder={setDateOrder} />)
    await userEvent.type(screen.getByText(/Ascending/), " ")
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})

it("shows issue summaries", async () => {
    const setShowIssueSummary = jest.fn();
    render(<SettingsPanel setShowIssueSummary={setShowIssueSummary} />)
    await act(async () => { fireEvent.click(screen.getAllByText(/Summary/)[0]) });
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})

it("shows issue summaries by keypress", async () => {
    const setShowIssueSummary = jest.fn();
    render(<SettingsPanel setShowIssueSummary={setShowIssueSummary} />)
    await userEvent.type(screen.getAllByText(/Summary/)[0], " ")
    expect(setShowIssueSummary).toHaveBeenCalledWith(true)
})
