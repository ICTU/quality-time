import React, { useEffect, useState } from 'react';
import { Tab, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { delete_metric, set_metric_attribute } from '../api/metric';
import { get_measurements } from '../api/measurement';
import { ChangeLog } from '../changelog/ChangeLog';
import { capitalize, get_source_name } from '../utils';
import { TrendTable } from '../trendTable/TrendTable';

function fetch_measurements(report_date, metric_uuid, setMeasurements) {
  get_measurements(metric_uuid, report_date)
    .then(function (json) {
      if (json.ok !== false) {
        setMeasurements(json.measurements);
      }
    })
}

export function MeasurementDetails(props) {
  const [measurements, setMeasurements] = useState([]);
  useEffect(() => {
    fetch_measurements(props.report_date, props.metric_uuid, setMeasurements);
    // eslint-disable-next-line
  }, [props.metric_uuid, props.report_date]);
  function reload() {
    props.reload();
    fetch_measurements(props.report_date, props.metric_uuid, setMeasurements)
  }
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const report_uuid = props.report.report_uuid;
  let panes = [];
  panes.push(
    {
      menuItem: <Menu.Item key='metric'><FocusableTab>{'Metric'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <MetricParameters metric={metric} {...props} />
        <ChangeLog report_uuid={report_uuid} timestamp={props.report.timestamp} metric_uuid={props.metric_uuid} />
      </Tab.Pane>
    },
    {
      menuItem: <Menu.Item key='sources'><FocusableTab>{'Sources'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane><Sources metric_type={metric.type} sources={metric.sources} {...props} /></Tab.Pane>
    }
  );
  if (measurements.length > 0) {
    panes.push(
      {
        menuItem: <Menu.Item key='trend_graph'><FocusableTab>{'Trend graph'}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane><TrendGraph unit={capitalize(props.unit)} title={props.metric_name} measurements={measurements} {...props} /></Tab.Pane>
      },
      {
        menuItem: <Menu.Item key='trend_table'><FocusableTab>{'Trend table'}</FocusableTab></Menu.Item>,
        render: () => (
          <Tab.Pane>
            <TrendTable
              datamodel={props.datamodel}
              reportDate={props.report_date}
              metrics={{[props.metric_uuid]: metric}}
              showTargets={true}
              measurements={measurements}
              trendTableInterval={props.trendTableInterval}
              setTrendTableInterval={props.setTrendTableInterval}
              trendTableNrDates={props.trendTableNrDates}
              setTrendTableNrDates={props.setTrendTableNrDates}
          />
          </Tab.Pane>
        )
      }
    );
    const last_measurement = measurements[measurements.length - 1];
    last_measurement.sources.forEach((source) => {
      const report_source = metric.sources[source.source_uuid];
      if (!report_source) { return }  // source was deleted, continue
      const nr_entities = (source.entities && source.entities.length) || 0;
      if (nr_entities === 0) { return } // no entities to show, continue
      const source_name = get_source_name(report_source, props.datamodel);
      panes.push({
        menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane><SourceEntities metric={metric} report_uuid={report_uuid} source={source} {...props} reload={reload} /></Tab.Pane>
      });
    });
  }

  function Buttons() {
    return (
      <ReadOnlyOrEditable editableComponent={
        <div style={{ marginTop: "20px" }}>
          <ReorderButtonGroup
            first={props.first_metric} last={props.last_metric} moveable="metric" slot="row"
            onClick={(direction) => { props.stop_sort(); set_metric_attribute(props.metric_uuid, "position", direction, props.reload) }} />
          <DeleteButton item_type="metric" onClick={() => delete_metric(props.metric_uuid, props.reload)} />
        </div>}
      />
    )
  }
  function onTabChange(event, data) {
    const old_tab = props.visibleDetailsTabs.filter((tab) => tab.startsWith(props.metric_uuid))[0];
    const new_tab = `${props.metric_uuid}:${data.activeIndex}`;
    props.toggleVisibleDetailsTab(old_tab, new_tab);
  }

  const visible_tabs = props.visibleDetailsTabs.filter((tab) => tab.startsWith(props.metric_uuid));
  const defaultActiveTab = visible_tabs.length > 0 ? Number(visible_tabs[0].split(":")[1]) : 0;
  return (
    <>
      <Tab panes={panes} defaultActiveIndex={defaultActiveTab} onTabChange={onTabChange} />
      <Buttons />
    </>
  );
}
