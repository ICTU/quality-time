import React from 'react';
import { shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subjects } from './Subjects';

const datamodel = { subjects: { subject_type: { name: "Subject type" } }, metrics: { metric_type: { tags: [] } } }
const report = { subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [], recent_measurements: [] } } } } };

let mockHistory = {};

function subjects() {
    return (
        shallow(<Subjects datamodel={datamodel} reports={[report]} report={report} subject_uuid="subject_uuid" tags={[]} history={mockHistory} />)
    )
}

describe("<Subjects />", () => {
    beforeEach(() => { mockHistory["replace"] = jest.fn(); mockHistory.location = {} });
    it('shows the subjects', () => {
        const wrapper = shallow(<Subjects datamodel={datamodel} reports={[report]} report={report} tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />);
        expect(wrapper.find("Subject").length).toBe(1);
    });
    it('shows the add subject button when editable', () => {
        const wrapper = shallow(<ReadOnlyContext.Provider value={false}>
            <Subjects datamodel={datamodel} reports={[report]} report={report} tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />
        </ReadOnlyContext.Provider>);
        expect(wrapper.find("Subjects").dive().find("ReadOnlyOrEditable").dive().find("ContextConsumer").dive().find("AddButton").prop("item_type")).toStrictEqual("subject");
    });
    it('hides metrics not requiring action', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("DropdownItem").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(true);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("DropdownItem").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
    });
    it('hides metrics not requiring action on load', () => {
        mockHistory.location.search = "?hide_metrics_not_requiring_action=true"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(true);
    });
    it('shows metrics not requiring action on load', () => {
        mockHistory.location.search = "?hide_metrics_not_requiring_action=false"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
    });
    it('hides columns', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("HideColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend'])
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("HideColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
    });
    it('hides columns on load', () => {
        mockHistory.location.search = "?hidden_columns=trend"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend'])
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("HideColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
    });
    it('hides multiple columns on load', () => {
        mockHistory.location.search = "?hidden_columns=trend,tags"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend', 'tags'])
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("HideColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['tags']);
    });
    it('can handle missing columns', () => {
        mockHistory.location.search = "?hidden_columns="
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([])
    });
    it('toggles tabs', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("visibleDetailsTabs")).toStrictEqual([]);
        wrapper.find("Subject").dive().find("Metric").dive().find("Measurement").dive().find("TableRowWithDetails").dive().find("TableCell").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("visibleDetailsTabs")).toStrictEqual(["metric_uuid:0"]);
        wrapper.find("Subject").dive().find("Metric").dive().find("Measurement").dive().find("TableRowWithDetails").dive().find("MeasurementDetails").dive().find("Tab").dive().find("Menu").dive().find("MenuItem").at(1).dive().find("a").simulate("click");
        expect(wrapper.find("Subject").prop("visibleDetailsTabs")).toStrictEqual(["metric_uuid:1"]);
        wrapper.find("Subject").dive().find("Metric").dive().find("Measurement").dive().find("TableRowWithDetails").dive().find("TableCell").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("visibleDetailsTabs")).toStrictEqual([]);
    });
    it('shows columns', () => {
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("visibleColumns")).toStrictEqual([]);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("ShowColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("visibleColumns")).toStrictEqual(['prev1']);
    });
    it('shows columns on load', () => {
        mockHistory.location.search = "?visible_columns=prev1"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("visibleColumns")).toStrictEqual(['prev1']);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("ShowColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("visibleColumns")).toStrictEqual([]);
    });
    it('sets the number of days earlier', () => {
        mockHistory.location.search = "?visible_columns=prev1"
        const wrapper = subjects();
        expect(wrapper.find("Subject").prop("previousMeasurementDaysEarlier")).toStrictEqual(3);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("DaysEarlierInput").dive().find("Input").simulate("change", {target: {value: 4}});
        expect(wrapper.find("Subject").prop("previousMeasurementDaysEarlier")).toStrictEqual(4);
    })
});