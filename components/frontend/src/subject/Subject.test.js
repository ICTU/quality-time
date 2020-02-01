import React from 'react';
import { mount, shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subject } from './Subject';

const datamodel = {
  subjects: {
    subject_type: { name: "Subject type"}
  },
  metrics: {
    metric_type: { name: "Metric type", tags: [] }
  }
}
const report = {
  subjects: {
    subject_uuid: {
      type: "subject_type", name: "Subject title", metrics: {
        metric_uuid: {
          type: "metric_type", tags: []
        },
        metric_uuidi2: {
          type: "metric_type", tags: []
        }
      }
    }
  }
};

describe("<Subject />", () => {
  it('shows the subject title', () => {
    const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
    expect(wrapper.find("SubjectTitle").length).toBe(1);
  });
  it('shows the add subject button', () => {
    const wrapper = mount(
      <ReadOnlyContext.Provider value={false}>
        <Subject datamodel={datamodel} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} />
      </ReadOnlyContext.Provider>
    );
    expect(wrapper.find("AddButton").length).toBe(1);
  });
  it('changes the sort column when clicked', () => {
    function table_header_cell() {
      return wrapper.find("SubjectTableHeader").at(0).dive().find("SortableHeader").at(0).dive().find("TableHeaderCell");
    }
    const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
    expect(table_header_cell().prop("sorted")).toBe(null);
    table_header_cell().simulate("click");
    expect(table_header_cell().prop("sorted")).toBe("ascending");
    table_header_cell().simulate("click");
    expect(table_header_cell().prop("sorted")).toBe("descending");
    table_header_cell().simulate("click");
    expect(table_header_cell().prop("sorted")).toBe(null);
  });
});