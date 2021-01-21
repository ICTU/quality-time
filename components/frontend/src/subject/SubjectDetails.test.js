import React from 'react';
import { mount, shallow } from 'enzyme';
import { Subject } from './Subject';
import { SubjectDetails } from './SubjectDetails';
import { Table } from 'semantic-ui-react';

const datamodel = {
  subjects: {
    subject_type: { name: "Subject type", metrics: ["metric_type"] }
  },
  metrics: {
    metric_type: { name: "Metric type", tags: [] }
  }
}
const report = {
  subjects: {
    subject_uuid: {
      type: "subject_type", name: "Subject 1 title", metrics: {
        metric_uuid: {
          name: "M1", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        },
        metric_uuidi2: {
          name: "M2", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        }
      }
    },
    subject_uuid2: {
      type: "subject_type", name: "Subject 2 title", metrics: {
        metric_uuid3: {
          name: "M3", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        }
      }
    }
  }
};

it('changes the sort column when clicked', () => {
  function table_header_cell(index) {
      const sortableHeader = wrapper.find("SortableHeader").at(index)
      const headerCell = sortableHeader.find("TableHeaderCell")
    return headerCell;
  }
  const wrapper = mount(
    <Table>
        <SubjectDetails 
            datamodel={datamodel}
            subject_uuid="subject_uuid" 
            metrics={report.subjects.subject_uuid.metrics} 
            report={report}
            hiddenColumns={[]}
            visibleDetailsTabs={[]} />
    </Table>);
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