import React from 'react';
import { mount } from 'enzyme';
import { SubjectDetails } from './SubjectDetails';
import { render } from '@testing-library/react';
import { datamodel, report } from "../__fixtures__/fixtures";

it('displays one row per metric', () => {
    const { queryAllByText } = render(
        <SubjectDetails
            datamodel={datamodel}
            subject_uuid="subject_uuid"
            metrics={report.subjects.subject_uuid.metrics}
            report={report}
            hiddenColumns={[]}
            visibleDetailsTabs={[]} />
    )
    expect(queryAllByText("M1").length).toBe(1)
    expect(queryAllByText("M2").length).toBe(1)
})

it('changes the sort column when clicked', () => {
    function table_header_cell(index) {
        const sortableHeader = wrapper.find("SortableHeader").at(index);
        return sortableHeader.find("TableHeaderCell");
    }
    const wrapper = mount(
        <SubjectDetails
            datamodel={datamodel}
            subject_uuid="subject_uuid"
            metrics={report.subjects.subject_uuid.metrics}
            report={report}
            hiddenColumns={[]}
            visibleDetailsTabs={[]} />
    );
    for (let index of [0, 1, 2, 3, 4, 5, 6, 7]) {
        expect(table_header_cell(index).prop("sorted")).toBe(null);
        table_header_cell(index).simulate("click");
        expect(table_header_cell(index).prop("sorted")).toBe("ascending");
        table_header_cell(index).simulate("click");
        expect(table_header_cell(index).prop("sorted")).toBe("descending");
        table_header_cell(index).simulate("click");
        expect(table_header_cell(index).prop("sorted")).toBe(null);
    }
});