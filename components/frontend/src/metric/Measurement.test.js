import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { Measurement } from './Measurement';

let report = {
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
          status: "target_not_met",
          value: "50",
          recent_measurements: [{sources: [{name: "Source", source_uuid: "1"}]}]
        }
      }
    }
  }
};
const data_model = {
  metrics: {
    stability: { name: "Stability", unit: "minutes", direction: "<", tags: [] },
    violations: { name: "Metric type", unit: "violations", direction: "<", tags: [] }
  }
};

function measurement() {
  return (
    mount(<Table><Table.Body><Measurement
      hiddenColumns={[]}
      report={report}
      reports={[report]}
      metric_uuid="metric_uuid"
      subject_uuid="subject_uuid"
      datamodel={data_model} /></Table.Body></Table>
    )
  )
}

it('renders the metric', () => {
  const wrapper = measurement();
  expect(wrapper.find("TableCell").at(1).text()).toBe("Metric");
  expect(wrapper.find("TableCell").at(4).text()).toBe("50 violations");
  expect(wrapper.find("TableCell").at(5).text()).toBe("≦ 0 violations");
  expect(wrapper.find("TableCell").at(6).find("SourceStatus").prop("source").name).toBe("Source");
});

it('renders the minutes', () => {
  report.subjects.subject_uuid.metrics.metric_uuid.type = "stability";
  const wrapper = measurement();
  expect(wrapper.find("TableCell").at(4).text()).toBe("0:50 minutes");
  expect(wrapper.find("TableCell").at(5).text()).toBe("≦ 0:00 minutes");
});

it('renders the minutes as percentage', () => {
  report.subjects.subject_uuid.metrics.metric_uuid.type = "stability";
  report.subjects.subject_uuid.metrics.metric_uuid.scale = "percentage";
  const wrapper = measurement();
  expect(wrapper.find("TableCell").at(4).text()).toBe("50% minutes");
  expect(wrapper.find("TableCell").at(5).text()).toBe("≦ 0% minutes");
});