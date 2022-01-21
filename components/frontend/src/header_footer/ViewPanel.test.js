import { act, fireEvent, render, screen } from '@testing-library/react';
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
        fireEvent.click(screen.getByText(/Hide metrics not requiring action/))
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
        fireEvent.click(screen.getByText(/Show all metrics/))
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
        fireEvent.click(screen.getByText(/Hide trend column/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
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
        fireEvent.click(screen.getByText(/Show trend column/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("sets the number of dates", async () => {
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
        fireEvent.click(screen.getByText(/7 dates/))
    });
    expect(setNrDates).toHaveBeenCalledWith(7)
})

it("set the date interval to weeks", async () => {
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

it("set the date interval to one day", async () => {
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
