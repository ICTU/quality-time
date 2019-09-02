import React from 'react';
import { Button, Icon, Popup, Tab, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { delete_metric, set_metric_attribute } from '../api/metric';
import { ChangeLog } from '../changelog/ChangeLog';

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
            readOnly={props.readOnly}
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
          <TrendGraph measurements={props.measurements} unit={unit_name} title={props.metric_name} />
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
          readOnly={props.readOnly}
          reload={props.reload}
          report_uuid={report_uuid}
        />
        <ChangeLog report={props.report} metric_uuid={props.metric_uuid} />
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
          readOnly={props.readOnly}
          reload={props.reload}
          report={props.report}
          sources={metric.sources}
        />
      </Tab.Pane>
    }
  );
  return (
    <>
      <Tab panes={panes} />
      {!props.readOnly &&
        <>
          <Button.Group style={{ marginTop: "10px" }}>
            <Popup content='Move metric to the first row' trigger={
              <Button
                aria-label="Move metric to the first row"
                basic
                disabled={props.first_metric}
                icon="angle double up"
                onClick={() => {
                  props.stop_sort();
                  set_metric_attribute(report_uuid, props.metric_uuid, "position", "first", props.reload)}
                }
                primary
              />}
            />
            <Popup content='Move metric one row up' trigger={
              <Button
                aria-label="Move metric one row up"
                basic
                disabled={props.first_metric}
                icon="angle up"
                onClick={() => {
                  props.stop_sort();
                  set_metric_attribute(report_uuid, props.metric_uuid, "position", "up", props.reload)}
                }
                primary
              />}
            />
            <Popup content='Move metric one row down' trigger={
              <Button
                aria-label="Move metric one row down"
                basic
                disabled={props.last_metric}
                icon="angle down"
                onClick={() => {
                  props.stop_sort();
                  set_metric_attribute(report_uuid, props.metric_uuid, "position", "down", props.reload)}
                }
                primary
              />}
            />
            <Popup content={`Move metric to the last row ${props.last_metric}`} trigger={
              <Button
                aria-label="Move metric to the last row"
                basic
                disabled={props.last_metric}
                icon="angle double down"
                onClick={() => {
                  props.stop_sort();
                  set_metric_attribute(report_uuid, props.metric_uuid, "position", "last", props.reload)}
                }
                primary
              />}
            />
          </Button.Group>
          <Button icon style={{ marginTop: "10px" }} floated='right' negative basic primary
            onClick={() => delete_metric(report_uuid, props.metric_uuid, props.reload)}>
            <Icon name='trash' /> Delete metric
          </Button>
        </>
      }
    </>
  )
}
