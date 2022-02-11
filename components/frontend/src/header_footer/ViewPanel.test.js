import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ViewPanel } from './ViewPanel';

it("clears the visible details tabs", async () => {
    const clearVisibleDetailsTabs = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                hiddenColumns={[]}
                visibleDetailsTabs={["tab"]}
            />
        )
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(clearVisibleDetailsTabs).toHaveBeenCalled()
})

it("doesn't clear the visible details tabs if there are none", async () => {
    const clearVisibleDetailsTabs = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                hiddenColumns={[]}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(clearVisibleDetailsTabs).not.toHaveBeenCalled()
})

it('resets the settings', async () => {
    const clearVisibleDetailsTabs = jest.fn();
    const clearHiddenColumns = jest.fn();
    const setDateInterval = jest.fn();
    const setDateOrder = jest.fn();
    const setHideMetricsNotRequiringAction = jest.fn();
    const setNrDates = jest.fn();
    const setSortColumn = jest.fn();
    const setSortDirection = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                clearHiddenColumns={clearHiddenColumns}
                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                dateInterval={14}
                dateOrder="ascending"
                hiddenColumns={["trend"]}
                hideMetricsNotRequiringAction={true}
                nrDates={7}
                setDateInterval={setDateInterval}
                setDateOrder={setDateOrder}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                setNrDates={setNrDates}
                setSortColumn={setSortColumn}
                setSortDirection={setSortDirection}
                sortColumn="status"
                sortDirection="descending"
                visibleDetailsTabs={["tab"]}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(clearVisibleDetailsTabs).toHaveBeenCalled()
    expect(clearHiddenColumns).toHaveBeenCalled()
    expect(setDateInterval).toHaveBeenCalled()
    expect(setDateOrder).toHaveBeenCalled()
    expect(setNrDates).toHaveBeenCalled()
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalled()
    expect(setSortColumn).toHaveBeenCalledWith(null)
    expect(setSortDirection).toHaveBeenCalledWith("ascending")
})

it('does not reset the settings when all have the default value', async () => {
    const clearVisibleDetailsTabs = jest.fn();
    const clearHiddenColumns = jest.fn();
    const setDateInterval = jest.fn();
    const setDateOrder = jest.fn();
    const setHideMetricsNotRequiringAction = jest.fn();
    const setNrDates = jest.fn();
    const setSortColumn = jest.fn();
    const setSortDirection = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                clearHiddenColumns={clearHiddenColumns}
                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                dateInterval={7}
                dateOrder="descending"
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={false}
                nrDates={1}
                setDateInterval={setDateInterval}
                setDateOrder={setDateOrder}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                setNrDates={setNrDates}
                sortColumn={null}
                sortDirection="ascending"
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(clearVisibleDetailsTabs).not.toHaveBeenCalled()
    expect(clearHiddenColumns).not.toHaveBeenCalled()
    expect(setDateInterval).not.toHaveBeenCalled()
    expect(setDateOrder).not.toHaveBeenCalled()
    expect(setNrDates).not.toHaveBeenCalled()
    expect(setHideMetricsNotRequiringAction).not.toHaveBeenCalled()
    expect(setSortColumn).not.toHaveBeenCalled()
    expect(setSortDirection).not.toHaveBeenCalled()
})

it("hides the metrics not requiring action", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={false}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/Metrics requiring action/))
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(true)
})

it("shows the metrics not requiring action", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={true}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/All metrics/))
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("shows the metrics not requiring action by keypress", async () => {
    const setHideMetricsNotRequiringAction = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={true}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                visibleDetailsTabs={[]}
            />
        )
        userEvent.type(screen.getByText(/All metrics/), "{Enter}")
    });
    expect(setHideMetricsNotRequiringAction).toHaveBeenCalledWith(false)
})

it("hides a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                toggleHiddenColumn={toggleHiddenColumn}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/Trend/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                toggleHiddenColumn={toggleHiddenColumn}
                visibleDetailsTabs={[]}
            />
        )
        userEvent.type(screen.getAllByText(/Comment/)[0], "{Enter}")
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={["trend"]}
                toggleHiddenColumn={toggleHiddenColumn}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/Trend/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("sets the number of dates", async () => {
    const setNrDates = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                nrDates={2}
                setNrDates={setNrDates}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/7 dates/))
    });
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("sets the number of dates by keypress", async () => {
    const setNrDates = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                nrDates={1}
                setNrDates={setNrDates}
                visibleDetailsTabs={[]}
            />
        )
        userEvent.type(screen.getByText(/5 dates/), "{Enter}")
    });
    expect(setNrDates).toHaveBeenCalledWith(5)
})

it("setss the date interval to weeks", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                dateInterval={1}
                setDateInterval={setDateInterval}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/2 weeks/))
    });
    expect(setDateInterval).toHaveBeenCalledWith(14)
})

it("sets the date interval to one day", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                dateInterval={7}
                setDateInterval={setDateInterval}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getByText(/1 day/))
    });
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sets the date interval by keypress", async () => {
    const setDateInterval = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                dateInterval={7}
                setDateInterval={setDateInterval}
                visibleDetailsTabs={[]}
            />
        )
        userEvent.type(screen.getByText(/1 day/), "{Enter}")
    });
    expect(setDateInterval).toHaveBeenCalledWith(1)
})

it("sorts the dates descending", async () => {
    const setDateOrder = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                dateOrder="ascending"
                setDateOrder={setDateOrder}
                visibleDetailsTabs={[]}
            />
        )
        fireEvent.click(screen.getAllByText(/Descending/)[1])
    });
    expect(setDateOrder).toHaveBeenCalledWith("descending")
})

it("sorts the dates ascending by keypress", async () => {
    const setDateOrder = jest.fn();
    await act(async () => {
        render(
            <ViewPanel
                hiddenColumns={[]}
                dateOrder="descending"
                setDateOrder={setDateOrder}
                visibleDetailsTabs={[]}
            />
        )
        userEvent.type(screen.getAllByText(/Ascending/)[1], "{Enter}")
    });
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})