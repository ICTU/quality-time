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
        userEvent.type(screen.getByText(/Comment/), "{Enter}")
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
                nrDates={1}
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
        fireEvent.click(screen.getByText(/Descending/))
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
        userEvent.type(screen.getByText(/Ascending/), "{Enter}")
    });
    expect(setDateOrder).toHaveBeenCalledWith("ascending")
})