import React, { Component } from 'react';
import { Button, Icon, Label, Tab, Table, Menu } from 'semantic-ui-react';
import { TrendGraph } from './TrendGraph';
import { Sources } from './Sources';
import { SourceUnits } from './SourceUnits';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from './FocusableTab';

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
    const panes = [];
    if (props.measurement !== null) {
      const unit_name = props.unit.charAt(0).toUpperCase() + props.unit.slice(1);
      props.measurement.sources.forEach((source) => {
        const report_source = metric.sources[source.source_uuid];
        if (!report_source) { return }  // source was deleted, continue
        const source_type = report_source.type;
        const source_name = report_source.name || props.datamodel.sources[source_type].name;
        let nr_units = source.value || 0;
        const nr_units_displayed = (source.units && source.units.length) || 0;
        if (nr_units_displayed === 0) { return } // no units to show
        if (Number(nr_units) !== Number(nr_units_displayed)) { nr_units = `${nr_units_displayed} of ${nr_units}` };
        panes.push({
          menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name} <Label basic circular color="grey">{nr_units}</Label></FocusableTab></Menu.Item>,
          render: () => <Tab.Pane>
            <SourceUnits
              datamodel={props.datamodel}
              ignore_unit={props.ignore_unit}
              metric={metric}
              metric_uuid={props.metric_uuid}
              readOnly={props.readOnly}
              report_uuid={props.report_uuid}
              set_rationale_for_ignoring_unit={props.set_rationale_for_ignoring_unit}
              source={source}
            />
          </Tab.Pane>
        });
      });
      panes.push(
        {
          menuItem: <Menu.Item key='trend'><FocusableTab>{'Trend'}</FocusableTab></Menu.Item>,
          render: () => <Tab.Pane>
            <TrendGraph measurements={props.measurements} unit={unit_name} />
          </Tab.Pane>
        }
      );
    }
    panes.push(
      {
        menuItem: <Menu.Item key='metric'><FocusableTab>{'Metric'}</FocusableTab></Menu.Item>,
        render: () => <Tab.Pane>
          <MetricParameters datamodel={props.datamodel} metric={metric}
            readOnly={props.readOnly} set_metric_attribute={props.set_metric_attribute} />
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
      <Table.Row>
        <Table.Cell colSpan="9">
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
