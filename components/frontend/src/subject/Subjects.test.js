import React from 'react';
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from '@testing-library/user-event';
import { mount } from 'enzyme';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from './Subjects';
import { DataModel } from '../context/Contexts';

const datamodel = {
    subjects: {
        subject_type: {
            name: "Subject type"
        }
    },
    metrics: {
        metric_type: {
            tags: []
        }
    }
}

const report = {
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject title",
            metrics: {
                metric_uuid: {
                    type: "metric_type",
                    tags: [],
                    recent_measurements: [],
                    sources: {}
                }
            }
        }
    }
};

let mockHistory = {};

function subjects() {
    return (
        mount(
            <DataModel.Provider value={datamodel}>
                <Subjects
                    hiddenColumns={[]}
                    history={mockHistory}
                    reports={[report]}
                    report={report}
                    subject_uuid="subject_uuid"
                    tags={[]}
                    toggleHiddenColumn={() => {/*Dummy implementation*/ }}
                    report_date={new Date()}
                />
            </DataModel.Provider>
        )
    )
}

function render_subjects(permissions = []) {
    return render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={datamodel}>
                <Subjects
                    hiddenColumns={[]}
                    history={{ location: {}, replace: () => {/* Dummy implementation */ } }}
                    report={report}
                    reports={[report]}
                    tags={[]}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    )
}


it("shows the subjects", () => {
    render_subjects();
    expect(screen.getAllByText(/Subject/).length).toBe(1);
})

it("shows the add subject button when editable", () => {
    render_subjects([EDIT_REPORT_PERMISSION]);
    expect(screen.getAllByText(/Add subject/).length).toBe(1);
})

it("does not show the add subject button when not editable", () => {
    render_subjects();
    expect(screen.queryByText(/Add subject/)).toBeNull();
})

it("hides metrics not requiring action", () => {
    render_subjects();
    userEvent.click(screen.getByRole("listbox"));
    expect(screen.getByText(/Hide metrics not requiring action/)).not.toBeNull()
    fireEvent.click(screen.getByText(/Hide metrics not requiring action/));
    fireEvent.click(screen.getByRole("listbox"));
    expect(screen.queryByText(/Hide metrics not requiring action/)).toBeNull()
    fireEvent.click(screen.getByText(/Show all metrics/));
    fireEvent.click(screen.getByRole("listbox"));
    expect(screen.getByText(/Hide metrics not requiring action/)).not.toBeNull()
})

describe("<Subjects />", () => {
    beforeEach(() => { mockHistory["replace"] = jest.fn(); mockHistory.location = {} });
    it('hides metrics not requiring action on load', () => {
        mockHistory.location.search = "?hide_metrics_not_requiring_action=true"
        const wrapper = subjects();
        expect(wrapper.find("Subjects").find("Subject").prop("hideMetricsNotRequiringAction")).toBe(true);
    });
    it('shows metrics not requiring action on load', () => {
        mockHistory.location.search = "?hide_metrics_not_requiring_action=false"
        const wrapper = subjects();
        expect(wrapper.find("Subjects").find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
    });
    it('toggles tabs', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subjects").find("Subject").prop("visibleDetailsTabs")).toStrictEqual([]);
        wrapper.find("Subjects").find("Subject").find("SubjectDetails").find("Metric").find("TableRowWithDetails").find("TableCell").at(0).simulate("click");
        expect(wrapper.find("Subjects").find("Subject").prop("visibleDetailsTabs")).toStrictEqual(["metric_uuid:0"]);
        wrapper.find("Subjects").find("Subject").find("SubjectDetails").find("Metric").find("TableRowWithDetails").find("MetricDetails").find("Tab").find("Menu").find("MenuItem").at(1).find("a").simulate("click");
        expect(wrapper.find("Subjects").find("Subject").prop("visibleDetailsTabs")).toStrictEqual(["metric_uuid:1"]);
        wrapper.find("Subjects").find("Subject").find("SubjectDetails").find("Metric").find("TableRowWithDetails").find("TableCell").at(0).simulate("click");
        expect(wrapper.find("Subjects").find("Subject").prop("visibleDetailsTabs")).toStrictEqual([]);
    });
    it('toggles subject trend table', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subjects").find("Subject").prop("subjectTrendTable")).toBe(false);
        wrapper.find("Subjects").find("Subject").find("SubjectDetails").find("SubjectTableHeader").find("HamburgerHeader").find("HamburgerItems").find("DropdownItem").at(1).simulate("click");
        expect(wrapper.find("Subjects").find("Subject").prop("subjectTrendTable")).toBe(true);
        wrapper.find("Subjects").find("Subject").find("TrendTable").find("TrendTableHeader").find("HamburgerMenu").find("HamburgerItems").find("DropdownItem").at(0).simulate("click");
        expect(wrapper.find("Subjects").find("Subject").prop("subjectTrendTable")).toBe(false);
    })
});
