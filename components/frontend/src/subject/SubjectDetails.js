import React, { useState } from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { Metric } from '../metric/Metric';
import { get_metric_name, get_metric_target, get_source_name } from '../utils';
import { HamburgerMenu } from '../widgets/HamburgerMenu';
import { SubjectFooter } from './SubjectFooter';


function createMetricComponents(props) {
  const subject = props.report.subjects[props.subject_uuid];
  const last_index = Object.entries(subject.metrics).length - 1;

  let components = [];
  Object.entries(props.metrics).forEach(([metric_uuid, metric], index) => {
    components.push(
      <Metric
        first_metric={index === 0}
        hiddenColumns={props.hiddenColumns}
        key={metric_uuid}
        last_metric={index === last_index}
        metric_uuid={metric_uuid}
        metric={metric}
        stop_sort={() => props.setSortColumn(null)}
        {...props}
      />)
  });
  return components
}

function sortMetricComponents(datamodel, metricComponents, sortDirection, sortColumn) {
  const status_order = { "": "0", target_not_met: "1", debt_target_met: "2", near_target_met: "3", target_met: "4" };
  const sorters = {
    name: (m1, m2) => {
      const attribute1 = get_metric_name(m1.props.metric, datamodel);
      const attribute2 = get_metric_name(m2.props.metric, datamodel);
      return attribute1.localeCompare(attribute2)
    },
    measurement: (m1, m2) => {
      const attribute1 = m1.props.metric.value || "";
      const attribute2 = m2.props.metric.value || "";
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
      const attribute1 = status_order[m1.props.metric.status || ""];
      const attribute2 = status_order[m2.props.metric.status || ""];
      return attribute1.localeCompare(attribute2)
    },
    source: (m1, m2) => {
      let m1_sources = Object.values(m1.props.metric.sources).map((source) => get_source_name(source, datamodel));
      m1_sources.sort();
      let m2_sources = Object.values(m2.props.metric.sources).map((source) => get_source_name(source, datamodel));
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
  metricComponents.sort(sorters[sortColumn]);
  if (sortDirection === 'descending') {
    metricComponents.reverse()
  }
}

export function SubjectDetails(props) {

  const [sortDirection, setSortDirection] = useState('ascending');
  const [sortColumn, setSortColumn] = useState(null);

  const metricComponents = createMetricComponents(props)
  if (sortColumn !== null) {
      sortMetricComponents(props.datamodel, metricComponents, sortDirection, sortColumn, setSortColumn)
  }

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
  
  function SortableHeader({ column, label, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
      <Table.HeaderCell onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
        {label}
      </Table.HeaderCell>
    )
  }
  
  function HamburgerHeader() {
    function ColumnMenuItem({ column }) {
      return (
        <Dropdown.Item onClick={() => props.toggleHiddenColumn(column)}>
          {props.hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Dropdown.Item>
      )
    }
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <HamburgerMenu>
          {props.extraHamburgerItems}
          <Dropdown.Header>Columns</Dropdown.Header>
          <ColumnMenuItem column="trend" />
          <ColumnMenuItem column="status" />
          <ColumnMenuItem column="measurement" />
          <ColumnMenuItem column="target" />
          <ColumnMenuItem column="source" />
          <ColumnMenuItem column="comment" />
          <ColumnMenuItem column="tags" />
        </HamburgerMenu>
      </Table.HeaderCell>
    )
  }
  
  function SubjectTableHeader() {
    return (
      <Table.Header>
        <Table.Row>
          <HamburgerHeader />
          <SortableHeader column='name' label='Metric' />
          {!props.hiddenColumns.includes("trend") && <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>}
          {!props.hiddenColumns.includes("status") && <SortableHeader column='status' label='Status' textAlign='center' />}
          {!props.hiddenColumns.includes("measurement") && <SortableHeader column='measurement' label='Measurement' />}
          {!props.hiddenColumns.includes("target") && <SortableHeader column='target' label='Target' />}
          {!props.hiddenColumns.includes("source") && <SortableHeader column='source' label='Source' />}
          {!props.hiddenColumns.includes("comment") && <SortableHeader column='comment' label='Comment' />}
          {!props.hiddenColumns.includes("tags") && <SortableHeader column='tags' label='Tags' />}
        </Table.Row>
      </Table.Header>
    )
  }

  return (
    <>
        <SubjectTableHeader />
        <Table.Body>{metricComponents}</Table.Body>
        <SubjectFooter 
          datamodel={props.datamodel} 
          subjectUuid={props.subject_uuid} 
          subject={props.report.subjects[props.subject_uuid]} 
          reload={props.reload} 
          reports={props.reports} 
          resetSortColumn={() => {setSortColumn(null)}} />
    </>
  )
}
