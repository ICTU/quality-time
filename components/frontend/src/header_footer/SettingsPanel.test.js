import { act, fireEvent, render, renderHook, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import history from 'history/browser';
import { SettingsPanel } from './SettingsPanel';
import {
    useDateIntervalURLSearchQuery,
    useDateOrderURLSearchQuery,
    useHiddenColumnsURLSearchQuery,
    useHiddenTagsURLSearchQuery,
    useMetricsToHideURLSearchQuery,
    useNrDatesURLSearchQuery,
    useShowIssueSummaryURLSearchQuery,
} from '../app_ui_settings';
import { createTestableSettings } from '../__fixtures__/fixtures';

beforeEach(() => {
    history.push("")
});

function renderSettingsPanel(
    {
        atReportsOverview = true,
        dateInterval = null,
        dateOrder = null,
        handleDateChange = jest.fn(),
        handleSort = jest.fn(),
        hiddenColumns = null,
        hiddenTags = null,
        metricsToHide = null,
        nrDates = null,
        reportDate = null,
        showIssueCreationDate = null,
        showIssueSummary = null,
        showIssueUpdateDate = null,
        showIssueDueDate = null,
        showIssueRelease = null,
        showIssueSprint = null,
        sortColumn = null,
        sortDirection = null,
        tags = [],
        visibleDetailsTabs = null
    } = {}
) {
    const settings = createTestableSettings()
    render(
        <SettingsPanel
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            handleSort={handleSort}
            settings={{
                dateInterval: dateInterval ?? settings.dateInterval,
                dateOrder: dateOrder ?? settings.dateOrder,
                hiddenColumns: hiddenColumns ?? settings.hiddenColumns,
                hiddenTags: hiddenTags ?? settings.hiddenTags,
                metricsToHide: metricsToHide ?? settings.metricsToHide,
                nrDates: nrDates ?? settings.nrDates,
                showIssueCreationDate: showIssueCreationDate ?? settings.showIssueCreationDate,
                showIssueSummary: showIssueSummary ?? settings.showIssueSummary,
                showIssueUpdateDate: showIssueUpdateDate ?? settings.showIssueUpdateDate,
                showIssueDueDate: showIssueDueDate ?? settings.showIssueDueDate,
                showIssueRelease: showIssueRelease ?? settings.showIssueRelease,
                showIssueSprint: showIssueSprint ?? settings.showIssueSprint,
                sortColumn: sortColumn ?? settings.sortColumn,
                sortDirection: sortDirection ?? settings.sortDirection,
                visibleDetailsTabs: visibleDetailsTabs ?? settings.visibleDetailsTabs
            }}
            reportDate={reportDate}
            tags={tags}
        />
    )
}

it('resets the settings', async () => {
    history.push(
        "?date_interval=2&date_order=ascending&hidden_columns=comment&hidden_tags=tag&metrics_to_hide=none&" +
        "nr_dates=2&show_issue_creation_date=true&show_issue_summary=true&show_issue_update_date=true&" +
        "show_issue_due_date=true&show_issue_release=true&show_issue_sprint=true&sort_column=status&" +
        "sort_direction=descending&tabs=tab"
    )
    const settings = createTestableSettings()
    const handleDateChange = jest.fn()
    renderSettingsPanel({
        handleDateChange: handleDateChange,
        reportDate: new Date("2023-01-01"),
        ...settings
    })
    Object.values(settings).forEach((setting) => expect(setting.isDefault()).not)
    fireEvent.click(screen.getByText(/Reset reports overview settings/))
    Object.values(settings).forEach((setting) => expect(setting.isDefault()))
    expect(handleDateChange).toHaveBeenCalledWith(null)
})

it('does not reset the settings when all have the default value', async () => {
    const settings = createTestableSettings()
    const handleDateChange = jest.fn()
    renderSettingsPanel({
        atReportsOverview: false,
        handleDateChange: handleDateChange,
        ...settings
    })
    Object.values(settings).forEach((setting) => expect(setting.isDefault()))
    fireEvent.click(screen.getByText(/Reset this report's settings/))
    Object.values(settings).forEach((setting) => expect(setting.isDefault()))
    expect(handleDateChange).not.toHaveBeenCalled()
})

it("hides the metrics not requiring action", async () => {
    const { result } = renderHook(() => useMetricsToHideURLSearchQuery())
    renderSettingsPanel({ metricsToHide: result.current })
    fireEvent.click(screen.getByText(/Metrics requiring action/))
    expect(result.current.value).toBe("no_action_needed")
})

it("shows all metrics", async () => {
    const { result } = renderHook(() => useMetricsToHideURLSearchQuery())
    renderSettingsPanel({ metricsToHide: result.current })
    fireEvent.click(screen.getByText(/All metrics/))
    expect(result.current.value).toBe("none")
})

it("shows all metrics by keypress", async () => {
    history.push("?metrics_to_hide=no_action_needed")
    const { result } = renderHook(() => useMetricsToHideURLSearchQuery())
    renderSettingsPanel({ metricsToHide: result.current })
    await userEvent.type(screen.getByText(/All metrics/), " ")
    expect(result.current.value).toBe("none")
})

it("hides a tag", async () => {
    const { result } = renderHook(() => useHiddenTagsURLSearchQuery())
    renderSettingsPanel({ tags: ["security"], hiddenTags: result.current })
    fireEvent.click(screen.getByText(/security/))
    expect(result.current.value).toStrictEqual(["security"])
})

it("hides a tag by keypress", async () => {
    const { result } = renderHook(() => useHiddenTagsURLSearchQuery())
    renderSettingsPanel({ tags: ["security"], hiddenTags: result.current })
    await userEvent.type(screen.getAllByText(/security/)[0], " ")
    expect(result.current.value).toStrictEqual(["security"])
})

it("shows a tag", async () => {
    history.push("?hidden_tags=security")
    const { result } = renderHook(() => useHiddenTagsURLSearchQuery())
    renderSettingsPanel({ tags: ["security"], hiddenTags: result.current })
    fireEvent.click(screen.getAllByText(/security/)[0])
    expect(result.current.value).toStrictEqual([])
})

it("hides a column", async () => {
    const { result } = renderHook(() => useHiddenColumnsURLSearchQuery())
    renderSettingsPanel({ hiddenColumns: result.current })
    fireEvent.click(screen.getByText(/Trend/))
    expect(result.current.value).toStrictEqual(["trend"])
})

it("hides a column by keypress", async () => {
    const { result } = renderHook(() => useHiddenColumnsURLSearchQuery())
    renderSettingsPanel({ hiddenColumns: result.current })
    await userEvent.type(screen.getAllByText(/Comment/)[0], " ")
    expect(result.current.value).toStrictEqual(["comment"])
})

it("shows a column", async () => {
    history.push("?hidden_columns=status")
    const { result } = renderHook(() => useHiddenColumnsURLSearchQuery())
    renderSettingsPanel({ hiddenColumns: result.current })
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(result.current.value).toStrictEqual([])
})

it("changes the sorting of an unsorted column", async () => {
    const handleSort = jest.fn();
    renderSettingsPanel({ handleSort: handleSort })
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
});

["ascending", "descending"].forEach((sortOrder) => {
    it("changes the sorting of a column", async () => {
        history.push(`?sort_column=comment&sort_direction=${sortOrder}`)
        const handleSort = jest.fn();
        renderSettingsPanel({ handleSort: handleSort })
        fireEvent.click(screen.getAllByText(/Comment/)[1])
        expect(handleSort).toHaveBeenCalledWith("comment")
    })
});

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    renderSettingsPanel({ handleSort: handleSort })
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    history.push("?hidden_columns=comment")
    const handleSort = jest.fn();
    renderSettingsPanel({ handleSort: handleSort })
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).not.toHaveBeenCalledWith("comment")
})

it("sets the number of dates", async () => {
    history.push("?nr_dates=2")
    const { result } = renderHook(() => useNrDatesURLSearchQuery())
    renderSettingsPanel({ nrDates: result.current })
    fireEvent.click(screen.getByText(/7 dates/))
    expect(result.current.value).toBe(7)
})

it("sets the number of dates by keypress", async () => {
    const { result } = renderHook(() => useNrDatesURLSearchQuery())
    renderSettingsPanel({ nrDates: result.current })
    await userEvent.type(screen.getByText(/5 dates/), " ")
    expect(result.current.value).toBe(5)
})

it("sets the date interval to weeks", async () => {
    history.push("?nr_dates=2")
    const dateInterval = renderHook(() => useDateIntervalURLSearchQuery())
    renderSettingsPanel({ dateInterval: dateInterval.result.current })
    await act(async () => fireEvent.click(screen.getByText(/2 weeks/)))
    expect(dateInterval.result.current.value).toBe(14)
})

it("sets the date interval to one day", () => {
    history.push("?nr_dates=2")
    const dateInterval = renderHook(() => useDateIntervalURLSearchQuery())
    renderSettingsPanel({ dateInterval: dateInterval.result.current })
    fireEvent.click(screen.getByText(/1 day/))
    expect(dateInterval.result.current.value).toBe(1)
})

it("sets the date interval by keypress", async () => {
    history.push("?nr_dates=2&date_interval=7")
    const dateInterval = renderHook(() => useDateIntervalURLSearchQuery())
    renderSettingsPanel({ dateInterval: dateInterval.result.current })
    await userEvent.type(screen.getByText(/1 day/), " ")
    expect(dateInterval.result.current.value).toBe(1)
})

it("sorts the dates descending", async () => {
    history.push("?nr_dates=2")
    const dateOrder = renderHook(() => useDateOrderURLSearchQuery())
    renderSettingsPanel({ dateOrder: dateOrder.result.current })
    await act(async () => fireEvent.click(screen.getByText(/Descending/)))
    expect(dateOrder.result.current.value).toBe("descending")
})

it("sorts the dates ascending by keypress", async () => {
    history.push("?nr_dates=2")
    const dateOrder = renderHook(() => useDateOrderURLSearchQuery("", "ascending"))
    renderSettingsPanel({ dateOrder: dateOrder.result.current })
    await userEvent.type(screen.getByText(/Ascending/), " ")
    expect(dateOrder.result.current.value).toBe("ascending")
})

it("shows issue summaries", async () => {
    const { result } = renderHook(() => useShowIssueSummaryURLSearchQuery())
    renderSettingsPanel({ showIssueSummary: result.current })
    await act(async () => { fireEvent.click(screen.getAllByText(/Summary/)[0]) });
    expect(result.current.value).toBe(true)
})

it("shows issue summaries by keypress", async () => {
    const { result } = renderHook(() => useShowIssueSummaryURLSearchQuery())
    renderSettingsPanel({ showIssueSummary: result.current })
    await userEvent.type(screen.getAllByText(/Summary/)[0], " ")
    expect(result.current.value).toBe(true)
})
