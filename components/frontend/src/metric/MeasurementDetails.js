import React from 'react';
import { Button, Icon, Tab, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { MoveButtonGroup} from '../widgets/MoveButton';
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
          changed_fields={props.changed_fields}
        />
      </Tab.Pane>
    }
  );
  return (
    <>
      <Tab panes={panes} />
      {!props.readOnly &&
        <>
          <MoveButtonGroup
            first={props.first_metric}
            last={props.last_metric}
            moveable="metric"
            onClick={(direction) => {
              props.stop_sort();
              set_metric_attribute(props.report.report_uuid, props.metric_uuid, "position", direction, props.reload)}
            }
            slot="row"
          />
          <Button icon style={{ marginTop: "10px" }} floated='right' negative basic primary
            onClick={() => delete_metric(report_uuid, props.metric_uuid, props.reload)}>
            <Icon name='trash' /> Delete metric
          </Button>
        </>
      }
    </>
  )
}
