import { fireEvent, render, renderHook, screen } from '@testing-library/react';
import history from 'history/browser';
import { useHiddenTagsURLSearchQuery } from '../app_ui_settings';
import { Report } from './Report';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';
import { mockGetAnimations } from '../dashboard/MockAnimations';
import { createTestableSettings } from '../__fixtures__/fixtures';

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    mockGetAnimations()
    history.push("")
});

afterEach(() => jest.restoreAllMocks())

const datamodel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ['metric_type'] }
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    }
}
const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject title", metrics: {
                metric_uuid: { name: "Metric name", type: "metric_type", tags: ["tag"], recent_measurements: [] },
                another_metric_uuid: { name: "Metric name", type: "metric_type", tags: ["other"], recent_measurements: [] },
            }
        }
    }
};

function renderReport(
    {
        reportToRender = null,
        dates = [new Date()],
        handleSort = jest.fn(),
        hiddenTags = null,
        report_date = null
    } = {}
) {
    let settings = createTestableSettings()
    if (hiddenTags) { settings.hiddenTags = hiddenTags }
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Report
                    dates={dates}
                    handleSort={handleSort}
                    lastUpdate={new Date()}
                    measurements={[]}
                    reports={[reportToRender]}
                    report={reportToRender}
                    report_date={report_date}
                    settings={settings}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('shows the report', async () => {
    renderReport({ reportToRender: report })
    expect(screen.getAllByText(/Subject title/).length).toBe(2)  // Once as dashboard card and once as subject header
});

it('shows an error message if there is no report', async () => {
    renderReport()
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
});

it('shows an error message if there was no report', async () => {
    renderReport({ report_date: new Date("2020-01-01") })
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
});

it('hides columns on load', async () => {
    history.push("?hidden_columns=status")
    renderReport({ reportToRender: report })
    expect(screen.queryByText(/Status/)).toBe(null)
});

it('sorts the column', async () => {
    let handleSort = jest.fn();
    renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('sorts the column descending', async () => {
    history.push("?sort_column=comment")
    let handleSort = jest.fn();
    renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('stops sorting', async () => {
    history.push("?sort_column=issues&sort_direction=descending")
    let handleSort = jest.fn();
    renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Issues/))
    expect(handleSort).toHaveBeenCalledWith("issues")
});

it('stop sorting on add metric', async () => {
    history.push("?sort_column=status")
    let handleSort = jest.fn();
    renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Add metric/))
    fireEvent.click(screen.getByText(/Metric type/))
    expect(handleSort).toHaveBeenCalledWith(null)
})

it('sorts another column', async () => {
    history.push("?sort_column=issues")
    let handleSort = jest.fn();
    renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('hides tags', async () => {
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    renderReport({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    fireEvent.click(screen.getAllByText(/tag/)[0])
    hiddenTags.rerender()
    expect(hiddenTags.result.current.value).toStrictEqual(["other"])
})

it('shows hidden tags', async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    renderReport({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expect(screen.queryAllByText("other").length).toBe(0)
    fireEvent.click(screen.getAllByText(/tag/)[0])
    hiddenTags.rerender()
    expect(hiddenTags.result.current.value).toStrictEqual([])
})

it('hides subjects if empty', async () => {
    history.push("?hidden_tags=tag,other")
    renderReport({ reportToRender: report })
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
})
