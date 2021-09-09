import React, { useEffect, useState } from 'react';
import { Header, Label, Menu, Tab } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { delete_metric, set_metric_attribute } from '../api/metric';
import { get_measurements } from '../api/measurement';
import { ChangeLog } from '../changelog/ChangeLog';
import { capitalize, get_source_name } from '../utils';

function fetch_measurements(report_date, metric_uuid, setMeasurements) {
  get_measurements(metric_uuid, report_date)
    .then(function (json) {
      if (json.ok !== false) {
        setMeasurements(json.measurements);
      }
    })
}

function MetricConfiguration({ datamodel, metric, metric_uuid, metric_type, report, reload }) {
  const panes = [
    {
      menuItem: <Menu.Item key='configuration'><FocusableTab>{'Configuration'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <MetricParameters datamodel={datamodel} metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
      </Tab.Pane>
    },
    {
      menuItem: <Menu.Item key='changelog'><FocusableTab>{'Changelog'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <ChangeLog report_uuid={report.report_uuid} timestamp={report.timestamp} metric_uuid={metric_uuid} />
      </Tab.Pane>
    }
  ];
  return (
    <>
      <Header>
        <Header.Content>
          {metric_type.name}
          <Header.Subheader>
            {metric_type.description}
          </Header.Subheader>
        </Header.Content>
      </Header>
      <Tab panes={panes} />
    </>
  )
}

export function MetricDetails({
  datamodel,
  report_date,
  reports,
  report,
  subject_uuid,
  metric_uuid,
  metric_name,
  metric_unit,
  first_metric,
  last_metric,
  measurement,
  scale,
  unit,
  stop_sort,
  changed_fields,
  visibleDetailsTabs,
  toggleVisibleDetailsTab,
  reload
}) {
  const [measurements, setMeasurements] = useState([]);
  useEffect(() => {
    fetch_measurements(report_date, metric_uuid, setMeasurements);
    // eslint-disable-next-line
  }, [metric_uuid, report_date]);
  function measurementsReload() {
    reload();
    fetch_measurements(report_date, metric_uuid, setMeasurements)
  }
  const metric = report.subjects[subject_uuid].metrics[metric_uuid];
  const last_measurement = measurements[measurements.length - 1];
  const any_error = last_measurement?.sources.some((source) => source.connection_error || source.parse_error);
  const sources_menu_item = any_error ? <Label color='red'>{"Sources"}</Label> : "Sources";
  let panes = [];
  panes.push(
    {
      menuItem: <Menu.Item key='metric'><FocusableTab>{'Metric'}</FocusableTab></Menu.Item>,
      render: () => <Tab.Pane>
        <MetricConfiguration
          datamodel={datamodel} metric={metric} metric_type={metric_type} metric_uuid={metric_uuid} report={report} reload={reload} />
      </Tab.Pane>
    },
    {
      menuItem: <Menu.Item key='sources'><FocusableTab>{sources_menu_item}</FocusableTab></Menu.Item>,
      render: () => (
        <Tab.Pane>
          <Sources
            datamodel={datamodel}
            reports={reports}
            report={report}
            metric_uuid={metric_uuid}
            metric_type={metric.type}
            metric_unit={metric_unit}
            sources={metric.sources}
            measurement={measurement}
            changed_fields={changed_fields}
            reload={reload} />
        </Tab.Pane>
      )
    }
  );
  if (measurements.length > 0) {
    if (metric.scale !== "version_number") {
      panes.push(
        {
          menuItem: <Menu.Item key='trend_graph'><FocusableTab>{'Trend graph'}</FocusableTab></Menu.Item>,
          render: () => <Tab.Pane><TrendGraph unit={capitalize(unit)} title={metric_name} measurements={measurements} scale={scale} /></Tab.Pane>
        }
      )
    }
    last_measurement.sources.forEach((source) => {
      const report_source = metric.sources[source.source_uuid];
      if (!report_source) { return }  // source was deleted, continue
      const nr_entities = (source.entities && source.entities.length) || 0;
      if (nr_entities === 0) { return } // no entities to show, continue
      const source_name = get_source_name(report_source, datamodel);
      panes.push({
        menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane><SourceEntities datamodel={datamodel} metric={metric} metric_uuid={metric_uuid} source={source} reload={measurementsReload} /></Tab.Pane>
      });
    });
  }

  function Buttons() {
    return (
      <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
        <div style={{ marginTop: "20px" }}>
          <ReorderButtonGroup
            first={first_metric} last={last_metric} moveable="metric" slot="row"
            onClick={(direction) => { stop_sort(); set_metric_attribute(metric_uuid, "position", direction, reload) }} />
          <DeleteButton item_type="metric" onClick={() => delete_metric(metric_uuid, reload)} />
        </div>}
      />
    )
  }
  function onTabChange(event, data) {
    const old_tab = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid))[0];
    const new_tab = `${metric_uuid}:${data.activeIndex}`;
    toggleVisibleDetailsTab(old_tab, new_tab);
  }

  const metric_type = datamodel.metrics[metric.type];
  const visible_tabs = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid));
  const defaultActiveTab = visible_tabs.length > 0 ? Number(visible_tabs[0].split(":")[1]) : 0;
  return (
    <>
      <Tab panes={panes} defaultActiveIndex={defaultActiveTab} onTabChange={onTabChange} />
      <Buttons />
    </>
  );
}
