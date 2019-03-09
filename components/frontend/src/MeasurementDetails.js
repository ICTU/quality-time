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
    fetch(`${window.server_url}/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}`, {
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
    const panes = [
      {
        menuItem: 'Metric', render: () => <Tab.Pane>
          <MetricParameters datamodel={props.datamodel} metric={props.metric}
            user={props.user} set_metric_attribute={props.set_metric_attribute} />
        </Tab.Pane>
      },
      {
        menuItem: 'Sources', render: () => <Tab.Pane>
          <Sources report_uuid={props.report_uuid} metric_uuid={props.metric_uuid} sources={props.metric.sources}
            measurement={props.measurement} user={props.user}
            metric_type={props.metric.type} datamodel={props.datamodel} reload={props.reload} />
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
            <SourcesUnits measurement={props.measurement} datamodel={props.datamodel} metric={props.metric}
              ignore_unit={props.ignore_unit} metric_uuid={props.metric_uuid} user={props.user}
              measurements={props.measurements} report_uuid={props.report_uuid} />
          </Tab.Pane>
        })
      }
    }
    return (
      <Table.Row>
        <Table.Cell colSpan="8">
          <Tab panes={panes} />
          {(props.user !== null) &&
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
