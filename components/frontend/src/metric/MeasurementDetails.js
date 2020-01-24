import React from 'react';
import { Dropdown, Icon, Tab, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { ItemActionButtons } from '../widgets/Button';
import { ItemBreadcrumb } from '../widgets/ItemBreadcrumb';
import { copy_metric, delete_metric, move_metric, set_metric_attribute } from '../api/metric';
import { ChangeLog } from '../changelog/ChangeLog';
import { get_source_name, get_subject_name } from '../utils';

function subject_options(reports, datamodel, current_subject_uuid) {
  let options = [];
    reports.forEach((report) => {
      Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const subject_name = get_subject_name(subject, datamodel);
        options.push({
          content: <ItemBreadcrumb report={report.title} subject={subject_name} />,
          disabled: subject_uuid === current_subject_uuid, key: subject_uuid,
          text: report.title + subject_name,
          value: subject_uuid
        })
      })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function MeasurementDetails(props) {
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const report_uuid = props.report.report_uuid;
  const panes = [];
  if (props.measurement) {
    props.measurement.sources.forEach((source) => {
      const report_source = metric.sources[source.source_uuid];
      if (!report_source) { return }  // source was deleted, continue
      const nr_entities = (source.entities && source.entities.length) || 0;
      if (nr_entities === 0) { return } // no entities to show, continue
      const source_name = get_source_name(report_source, props.datamodel);
      panes.push({
        menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane><SourceEntities metric={metric} report_uuid={report_uuid} source={source} {...props} /></Tab.Pane>
      });
    });
  }
  if (props.measurements.length > 0) {
    const unit_name = props.unit.charAt(0).toUpperCase() + props.unit.slice(1);
    panes.push(
      {
        menuItem: <Menu.Item key='trend'><FocusableTab>{'Trend'}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane><TrendGraph unit={unit_name} title={props.metric_name} {...props} /></Tab.Pane>
      }
    );
  }
  panes.push(
    {
      menuItem: <Menu.Item key='metric'><FocusableTab>{'Metric'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <MetricParameters metric={metric} {...props} />
        <ChangeLog report_uuid={report_uuid} timestamp={props.report.timestamp} metric_uuid={props.metric_uuid} />
      </Tab.Pane>
    }
  );
  panes.push(
    {
      menuItem: <Menu.Item key='sources'><FocusableTab>{'Sources'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane><Sources metric_type={metric.type} sources={metric.sources} {...props} /></Tab.Pane>
    }
  );

  function Buttons() {
    return (
      <ReadOnlyOrEditable editableComponent={
        <div style={{ marginTop: "20px" }}>
          <ItemActionButtons
            item_type="metric"
            first_item={props.first_metric}
            last_item={props.last_metric}
            onCopy={() => copy_metric(props.metric_uuid, props.reload)}
            onDelete={() => delete_metric(props.metric_uuid, props.reload)}
            onMove={(subject_uuid) => move_metric(props.metric_uuid, subject_uuid, props.reload)}
            onReorder={(direction) => {
              props.stop_sort();
              set_metric_attribute(props.metric_uuid, "position", direction, props.reload)
            }}
            options={subject_options(props.reports, props.datamodel, props.subject_uuid)}
            reorder_header={<Dropdown.Header>Report <Icon name='right chevron'/>Subject</Dropdown.Header>}
            slot="row"
          />
        </div>}
      />
    )
  }
  return (
    <>
      <Tab panes={panes} />
      <Buttons />
    </>
  )
}
