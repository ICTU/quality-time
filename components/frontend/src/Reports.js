import React, { Component } from 'react';
import { Button, Card, Icon, Segment } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';


function ReportCard(props) {
  const summary = props.report.summary;
  const nr_metrics = summary.red + summary.green + summary.yellow;
  return (
    <Card onClick={(e) => props.open_report(e, props.report)}>
      <StatusPieChart red={summary.red} green={summary.green} yellow={summary.yellow} />
      <Card.Content>
        <Card.Header>{props.report.title}</Card.Header>
        <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
      </Card.Content>
    </Card>
  )
}

class Reports extends Component {
  add_report(event) {
    event.preventDefault();
    const self = this;
    fetch(`http://localhost:8080/reports/new`, {
      method: 'post',
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
    return (
      <>
        <Card.Group itemsPerRow={6}>
          {this.props.reports.map((report) =>
            <ReportCard key={report.report_uuid} report={report} open_report={this.props.open_report} />)
          }
        </Card.Group>
        {(this.props.user !== null) &&
        <Segment basic>
          <Button icon primary basic onClick={(e) => this.add_report(e)}>
            <Icon name='plus' /> Add report
          </Button>
        </Segment>}
      </>
    )
  }
}

export { Reports };
