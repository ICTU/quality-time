import React, { Component } from 'react';
import { Button, Icon, Tab, Table } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { Sources } from './Sources';
import { SourcesUnits } from './SourcesUnits';
import { MetricParameters } from './MetricParameters';

class MeasurementDetails extends Component {
  delete_metric(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/metric/${this.props.metric_uuid}`, {
      method: 'delete',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(
      () => self.props.reload()
    );
  }
  render() {
    const props = this.props;
    const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
    const panes = [
      {
        menuItem: 'Metric', render: () => <Tab.Pane>
          <MetricParameters datamodel={props.datamodel} metric={metric}
            readOnly={props.readOnly} set_metric_attribute={props.set_metric_attribute} />
        </Tab.Pane>
      },
      {
        menuItem: 'Sources', render: () => <Tab.Pane>
          <Sources
            datamodel={props.datamodel}
            measurement={props.measurement}
            metric_type={metric.type}
            metric_uuid={props.metric_uuid}
            readOnly={props.readOnly}
            reload={props.reload}
            report={props.report}
            sources={metric.sources}
          />
        </Tab.Pane>
      }
    ];
    if (props.measurement !== null) {
      const unit_name = props.unit.charAt(0).toUpperCase() + props.unit.slice(1);
      panes.push(
        {
          menuItem: 'Trend', render: () => <Tab.Pane>
            <TrendGraph measurements={props.measurements} unit={unit_name} />
          </Tab.Pane>
        });
      const nr_units = props.measurement.sources.reduce((nr_units, source) => nr_units + (source.units && source.units.length) || 0, 0);
      if (nr_units > 0) {
        panes.push({
          menuItem: unit_name, render: () => <Tab.Pane>
            <SourcesUnits measurement={props.measurement} datamodel={props.datamodel} metric={metric}
              ignore_unit={props.ignore_unit} metric_uuid={props.metric_uuid} readOnly={props.readOnly}
              measurements={props.measurements} report_uuid={props.report_uuid} />
          </Tab.Pane>
        })
      }
    }
    return (
      <Table.Row>
        <Table.Cell colSpan="8">
          <Tab panes={panes} />
          {!props.readOnly &&
            <Button icon style={{ marginTop: "10px" }} floated='right' negative basic primary
              onClick={(e) => this.delete_metric(e)}>
              <Icon name='trash' /> Delete metric
            </Button>}
        </Table.Cell>
      </Table.Row>
    )
  }
}

export { MeasurementDetails };
