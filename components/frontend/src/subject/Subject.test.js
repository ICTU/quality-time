import React from 'react';
import { mount, shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subject } from './Subject';

const datamodel = {
  subjects: {
    subject_type: { name: "Subject type" }
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
          type: "metric_type", tags: [], sources: {}, recent_measurements: []
        },
        metric_uuidi2: {
          type: "metric_type", tags: [], sources: {}, recent_measurements: []
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
    function table_header_cell(index) {
      return wrapper.find("SubjectTableHeader").at(0).dive().find("SortableHeader").at(index).dive().find("TableHeaderCell");
    }
    const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
    for (let index of [0, 1, 2, 3, 4, 5, 6]) {
      expect(table_header_cell(index).prop("sorted")).toBe(null);
      table_header_cell(index).simulate("click");
      expect(table_header_cell(index).prop("sorted")).toBe("ascending");
      table_header_cell(index).simulate("click");
      expect(table_header_cell(index).prop("sorted")).toBe("descending");
      table_header_cell(index).simulate("click");
      expect(table_header_cell(index).prop("sorted")).toBe(null);
    }
  });
});