import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { Measurement } from './Measurement';

const report = {
  report_uuid: "report_uuid",
  subjects: {
    subject_uuid: {
      name: "Subject",
      metrics: {
        metric_uuid: {
          name: "Metric",
          accept_debt: false,
          tags: [],
          type: "violations",
          sources: [],
          status: null,
          recent_measurements: [{sources: [{name: "Source", source_uuid: "1"}]}]
        }
      }
    }
  }
};
const data_model = { metrics: { violations: { name: "Metric type", direction: "<", tags: [] } } };

it('renders the source', () => {
  const wrapper = mount(<Table><Table.Body><Measurement
    hiddenColumns={[]}
    report={report}
    reports={[report]}
    metric_uuid="metric_uuid"
    subject_uuid="subject_uuid"
    datamodel={data_model} /></Table.Body></Table>);
  expect(wrapper.find("TableCell").at(6).find("SourceStatus").prop("source").name).toBe("Source");
});

it('renders the metric name', () => {
  const wrapper = mount(<Table><Table.Body><Measurement
    hiddenColumns={[]}
    report={report}
    reports={[report]}
    metric_uuid="metric_uuid"
    subject_uuid="subject_uuid"
    datamodel={data_model} /></Table.Body></Table>);
  expect(wrapper.find("TableCell").at(1).text()).toBe("Metric");
});