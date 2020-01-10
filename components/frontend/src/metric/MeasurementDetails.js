import React from 'react';
import { Tab, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { ItemActionButtons } from '../widgets/Button';
import { copy_metric, delete_metric, move_metric, set_metric_attribute } from '../api/metric';
import { ChangeLog } from '../changelog/ChangeLog';

function subject_options(reports, datamodel, current_subject_uuid) {
  let subject_options = [];
    reports.forEach((report) => {
      Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        subject_options.push({
          disabled: subject_uuid === current_subject_uuid, key: subject_uuid,
          text: report.title + " / " + (subject.name || datamodel.subjects[subject.type].name), value: subject_uuid
        })
      })
    });
    subject_options.sort((a, b) => a.text.localeCompare(b.text));
    return subject_options;
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
      const source_type = report_source.type;
      const source_name = report_source.name || props.datamodel.sources[source_type].name;
      panes.push({
        menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane>
          <SourceEntities
            datamodel={props.datamodel}
            fetch_measurement_and_reload={props.fetch_measurement_and_reload}
            metric={metric}
            metric_uuid={props.metric_uuid}
            report_uuid={report_uuid}
            source={source}
          />
        </Tab.Pane>
      });
    });
  }
  if (props.measurements.length > 0) {
    const unit_name = props.unit.charAt(0).toUpperCase() + props.unit.slice(1);
    panes.push(
      {
        menuItem: <Menu.Item key='trend'><FocusableTab>{'Trend'}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane>
          <TrendGraph measurements={props.measurements} unit={unit_name} scale={props.scale} title={props.metric_name} />
        </Tab.Pane>
      }
    );
  }
  panes.push(
    {
      menuItem: <Menu.Item key='metric'><FocusableTab>{'Metric'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <MetricParameters
          datamodel={props.datamodel}
          fetch_measurement_and_reload={props.fetch_measurement_and_reload}
          metric={metric}
          metric_uuid={props.metric_uuid}
          reload={props.reload}
        />
        <ChangeLog report_uuid={report_uuid} timestamp={props.report.timestamp} metric_uuid={props.metric_uuid} />
      </Tab.Pane>
    }
  );
  panes.push(
    {
      menuItem: <Menu.Item key='sources'><FocusableTab>{'Sources'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <Sources
          datamodel={props.datamodel}
          measurement={props.measurement}
          metric_type={metric.type}
          metric_unit={props.unit}
          metric_uuid={props.metric_uuid}
          reload={props.reload}
          report={props.report}
          reports={props.reports}
          sources={metric.sources}
          changed_fields={props.changed_fields}
        />
      </Tab.Pane>
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
