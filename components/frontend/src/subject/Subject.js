import React, { useState } from 'react';
import { Dropdown, Input, Table } from 'semantic-ui-react';
import { Metric } from '../metric/Metric';
import { SubjectTitle } from './SubjectTitle';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CopyButton, AddButton, MoveButton } from '../widgets/Button';
import { add_metric, copy_metric, move_metric } from '../api/metric';
import { get_metric_name, get_metric_target, get_source_name } from '../utils';
import { metric_options } from '../widgets/menu_options';

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

  function create_metric_components() {
    let components = [];
    Object.entries(subject.metrics).forEach(([metric_uuid, metric], index) => {
      const status = metric.status;
      if (props.hideMetricsNotRequiringAction && (status === "target_met" || status === "debt_target_met")) { return }
      if (props.tags.length > 0 && props.tags.filter(value => metric.tags.includes(value)).length === 0) { return }
      components.push(
        <Metric
          first_metric={index === 0}
          hiddenColumns={props.hiddenColumns}
          key={metric_uuid}
          last_metric={index === last_index}
          metric_uuid={metric_uuid}
          metric={metric}
          previousMeasurementDaysAgo={previousMeasurementDaysAgo}
          stop_sort={() => setSortColumn(null)}
          visibleColumns={props.visibleColumns}
          {...props}
        />)
    });
    return components
  }
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('ascending');
  const [previousMeasurementDaysAgo, setPreviousMeasurementDaysAgo] = useState(3);
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
  function SortableHeader({ children, column, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
      <Table.HeaderCell onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
        {children}
      </Table.HeaderCell>
    )
  }
  function HamburgerHeader() {
    function HideColumnMenuItem({ column, header }) {
      let column_header = header || column;
      return (
        <Dropdown.Item onClick={() => props.toggleHiddenColumn(column)}>
          {props.hiddenColumns.includes(column) ? `Show ${column_header} column` : `Hide ${column_header} column`}
        </Dropdown.Item>
      )
    }
    function ShowColumnMenuItem({ column, header }) {
      let column_header = header || column;
      return (
        <Dropdown.Item onClick={() => props.toggleVisibleColumn(column)}>
          {props.visibleColumns.includes(column) ? `Hide ${column_header} column` : `Show ${column_header} column`}
        </Dropdown.Item>
      )
    }
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <Dropdown item icon='sidebar'>
          <Dropdown.Menu>
            <Dropdown.Header>Rows</Dropdown.Header>
            <Dropdown.Item onClick={() => props.setHideMetricsNotRequiringAction(!props.hideMetricsNotRequiringAction)}>
              {props.hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
            </Dropdown.Item>
            <Dropdown.Header>Columns</Dropdown.Header>
            <HideColumnMenuItem column="trend"/>
            <HideColumnMenuItem column="status"/>
            <HideColumnMenuItem column="measurement"/>
            <ShowColumnMenuItem column="prev1" header="earlier measurement" />
            <HideColumnMenuItem column="target"/>
            <HideColumnMenuItem column="source"/>
            <HideColumnMenuItem column="comment"/>
            <HideColumnMenuItem column="tags"/>
          </Dropdown.Menu>
        </Dropdown>
      </Table.HeaderCell>
    )
  }
  function DaysAgoInput() {
    return (
      <Input inline style={{ width: 35 }} transparent type='number' value={previousMeasurementDaysAgo}
        tabIndex={0} onChange={({ value }) => { setPreviousMeasurementDaysAgo(Math.min(7, Math.max(1, value))) }} />
    )
  }
  function SubjectTableHeader() {
    const measurement_header = props.report_date ? `Measurement (${props.report_date.toLocaleDateString()})` : 'Measurement'
    return (
      <Table.Header>
        <Table.Row>
          <HamburgerHeader />
          <SortableHeader column='name'>Metric</SortableHeader>
          {!props.hiddenColumns.includes("trend") && <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>}
          {!props.hiddenColumns.includes("status") && <SortableHeader column='status' textAlign='center' >Status</SortableHeader>}
          {!props.hiddenColumns.includes("measurement") && <SortableHeader column='measurement'>{measurement_header}</SortableHeader>}
          {props.visibleColumns.includes("prev1") && <Table.HeaderCell>Measurement <DaysAgoInput /> day{previousMeasurementDaysAgo === 1 ? '' : 's'} earlier</Table.HeaderCell>}
          {!props.hiddenColumns.includes("target") && <SortableHeader column='target'>Target</SortableHeader>}
          {!props.hiddenColumns.includes("source") && <SortableHeader column='source'>Source</SortableHeader>}
          {!props.hiddenColumns.includes("comment") && <SortableHeader column='comment'>Comment</SortableHeader>}
          {!props.hiddenColumns.includes("tags") && <SortableHeader column='tags'>Tags</SortableHeader>}
        </Table.Row>
      </Table.Header>
    )
  }
  function SubjectTableFooter() {
    return (
      <ReadOnlyOrEditable editableComponent={
        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell colSpan='10'>
              <AddButton item_type="metric" onClick={() => {
                setSortColumn(null);
                add_metric(props.subject_uuid, props.reload);
              }}
              />
              <CopyButton
                item_type="metric"
                onChange={(source_metric_uuid) => {
                  setSortColumn(null);
                  copy_metric(source_metric_uuid, props.subject_uuid, props.reload);
                }}
                get_options={() => metric_options(props.reports, props.datamodel, subject.type)}
              />
              <MoveButton
                item_type="metric"
                onChange={(source_metric_uuid) => {
                  setSortColumn(null);
                  move_metric(source_metric_uuid, props.subject_uuid, props.reload);
                }}
                get_options={() => metric_options(props.reports, props.datamodel, subject.type, props.subject_uuid)}
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
