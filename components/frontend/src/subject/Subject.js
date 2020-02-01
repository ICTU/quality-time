import React, { useState } from 'react';
import { Button, Popup, Table } from 'semantic-ui-react';
import { Metric } from '../metric/Metric';
import { SubjectTitle } from './SubjectTitle';
import { add_metric } from '../api/metric';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton } from '../widgets/Button';
import { get_metric_name, get_metric_target, get_source_name } from '../utils';

export function Subject(props) {
  function handleSort(column) {
    if (sortColumn === column) {
      if (sortDirection === 'descending') {
        setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
      }
      setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
    } else {
      setSortColumn(column)
    }
  }

  const subject = props.report.subjects[props.subject_uuid];
  const last_index = Object.entries(subject.metrics).length - 1;

  function get_last_measurement(metric, metric_uuid) {
    const measurement = lastMeasurements[metric_uuid];
    if (measurement) {
      const scale = metric.scale || props.datamodel.metrics[metric.type].default_scale || "count";
      return measurement[scale] || {value: measurement.value || "", status: measurement.status || ""};
    }
    return {value: "", status: ""}
  }

  function create_metric_components() {
    let metric_components = [];
    Object.entries(subject.metrics).forEach(([metric_uuid, metric], index) => {
      const status = get_last_measurement(metric, metric_uuid).status;
      if (props.hideMetricsNotRequiringAction && (status === "target_met" || status === "debt_target_met")) { return }
      if (props.tags.length > 0 && props.tags.filter(value => metric.tags.includes(value)).length === 0) { return }
      metric_components.push(
        <Metric
          first_metric={index === 0}
          key={metric_uuid}
          last_metric={index === last_index}
          metric_uuid={metric_uuid}
          metric={metric}
          set_last_measurement={(m, l) => setLastMeasurements(lm => ({ ...lm, [m]: l }))}
          stop_sort={() => setSortColumn(null)}
          {...props}
        />)
    });
    return metric_components
  }
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('ascending');
  const [lastMeasurements, setLastMeasurements] = useState({});
  const metric_components = create_metric_components();

  if (sortColumn !== null) {
    const status_order = { "": "0", target_not_met: "1", debt_target_met: "2", near_target_met: "3", target_met: "4" };
    const sorters = {
      name: (m1, m2) => {
        const attribute1 = get_metric_name(m1.props.metric, props.datamodel);
        const attribute2 = get_metric_name(m2.props.metric, props.datamodel);
        return attribute1.localeCompare(attribute2)
      },
      measurement: (m1, m2) => {
        const attribute1 = get_last_measurement(m1.props.metric, m1.props.metric_uuid).value || "";
        const attribute2 = get_last_measurement(m2.props.metric, m2.props.metric_uuid).value || "";
        return attribute1.localeCompare(attribute2)
      },
      target: (m1, m2) => {
        const attribute1 = get_metric_target(m1.props.metric);
        const attribute2 = get_metric_target(m2.props.metric);
        return attribute1.localeCompare(attribute2)
      },
      comment: (m1, m2) => {
        const attribute1 = m1.props.metric.comment || '';
        const attribute2 = m2.props.metric.comment || '';
        return attribute1.localeCompare(attribute2)
      },
      status: (m1, m2) => {
        const attribute1 = status_order[get_last_measurement(m1.props.metric, m1.props.metric_uuid).status || ""];
        const attribute2 = status_order[get_last_measurement(m2.props.metric, m2.props.metric_uuid).status || ""];
        return attribute1.localeCompare(attribute2)
      },
      source: (m1, m2) => {
        let m1_sources = Object.values(m1.props.metric.sources).map((source) => get_source_name(source, props.datamodel));
        m1_sources.sort();
        let m2_sources = Object.values(m2.props.metric.sources).map((source) => get_source_name(source, props.datamodel));
        m2_sources.sort();
        const attribute1 = m1_sources.length > 0 ? m1_sources[0] : '';
        const attribute2 = m2_sources.length > 0 ? m2_sources[0] : '';
        return attribute1.localeCompare(attribute2)
      },
      tags: (m1, m2) => {
        let m1_tags = m1.props.metric.tags;
        m1_tags.sort();
        let m2_tags = m2.props.metric.tags;
        m2_tags.sort();
        const attribute1 = m1_tags.length > 0 ? m1_tags[0] : '';
        const attribute2 = m2_tags.length > 0 ? m2_tags[0] : '';
        return attribute1.localeCompare(attribute2)
      }
    }
    metric_components.sort(sorters[sortColumn]);
    if (sortDirection === 'descending') {
      metric_components.reverse()
    }
  }
  function SortableHeader({ column, label }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
      <Table.HeaderCell onClick={() => handleSort(column)} sorted={sorted}>
        {label}
      </Table.HeaderCell>
    )
  }
  function FilterHeader() {
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <Popup trigger={
          <Button
            basic
            compact
            icon={props.hideMetricsNotRequiringAction ? 'unhide' : 'hide'}
            onClick={() => props.setHideMetricsNotRequiringAction(!props.hideMetricsNotRequiringAction)}
            primary
          />
        } content={props.hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'} />
      </Table.HeaderCell>
    )
  }
  function SubjectTableHeader() {
    return (
      <Table.Header>
        <Table.Row>
          <FilterHeader/>
          <SortableHeader column='name' label='Metric' />
          <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>
          <SortableHeader column='status' label='Status' />
          <SortableHeader column='measurement' label='Measurement' />
          <SortableHeader column='target' label='Target' />
          <SortableHeader column='source' label='Source' />
          <SortableHeader column='comment' label='Comment' />
          <SortableHeader column='tags' label='Tags' />
        </Table.Row>
      </Table.Header>
    )
  }
  function SubjectTableFooter() {
    return (
      <ReadOnlyOrEditable editableComponent={
        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell colSpan='9'>
              <AddButton
                item_type={"metric"}
                onClick={() => {
                  setSortColumn(null);
                  add_metric(props.subject_uuid, props.reload);
                }}
              />
            </Table.HeaderCell>
          </Table.Row>
        </Table.Footer>}
      />
    )
  }
  return (
    <div id={props.subject_uuid}>
      <SubjectTitle subject={subject} {...props} />
      <Table sortable>
        <SubjectTableHeader />
        <Table.Body>{metric_components}</Table.Body>
        <SubjectTableFooter />
      </Table>
    </div>
  )
}
