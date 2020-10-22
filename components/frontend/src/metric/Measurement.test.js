import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { Measurement } from './Measurement';

const data_model = {
  metrics: {
    stability: { name: "Stability", unit: "minutes", direction: "<", tags: [] },
    violations: { name: "Metric type", unit: "violations", direction: "<", tags: [] }
  }
};

let report;

beforeEach(() => {
  report = {
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
            scale: "count",
            value: "50",
            recent_measurements: [{ sources: [{ name: "Source", source_uuid: "1" }] }]
          }
        }
      }
    }
  }
});

function measurement(visibleColumns = []) {
  return (
    mount(
      <Table>
        <Table.Body>
          <Measurement
            datamodel={data_model}
            hiddenColumns={[]}
            metric_uuid="metric_uuid"
            previousMeasurementDaysEarlier={3}
            report={report}
            reports={[report]}
            subject_uuid="subject_uuid"
            visibleColumns={visibleColumns}
            visibleDetailsTabs={[]}
          />
        </Table.Body>
      </Table>
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
  expect(wrapper.find("TableCell").at(4).text()).toBe("0:50 hours");
  expect(wrapper.find("TableCell").at(5).text()).toBe("≦ 0:00 hours");
});

it('renders the minutes as percentage', () => {
  report.subjects.subject_uuid.metrics.metric_uuid.type = "stability";
  report.subjects.subject_uuid.metrics.metric_uuid.scale = "percentage";
  const wrapper = measurement();
  expect(wrapper.find("TableCell").at(4).text()).toBe("50% minutes");
  expect(wrapper.find("TableCell").at(5).text()).toBe("≦ 0% minutes");
});

it('renders the previous measurement column without measurement', () => {
  const wrapper = measurement(['prev1']);
  expect(wrapper.find("TableCell").at(5).text()).toBe("? violations");
});

it('renders the previous measurement column with measurement', () => {
  let four_days_ago = new Date();
  four_days_ago.setDate(four_days_ago.getDate() - 4);
  const now = new Date();
  report.subjects.subject_uuid.metrics.metric_uuid.recent_measurements[0].start = four_days_ago.toISOString();
  report.subjects.subject_uuid.metrics.metric_uuid.recent_measurements[0].end = now.toISOString();
  report.subjects.subject_uuid.metrics.metric_uuid.recent_measurements[0].count = { value: 50 };
  const wrapper = measurement(['prev1']);
  expect(wrapper.find("TableCell").at(5).text()).toBe("50 violations");
});
