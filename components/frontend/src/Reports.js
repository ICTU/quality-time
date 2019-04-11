import React, { Component } from 'react';
import { Button, Card, Icon, Segment } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';


function ReportCard(props) {
  const summary = props.report.summary;
  const nr_metrics = summary.red + summary.green + summary.yellow + summary.grey;
  return (
    <Card onClick={(e) => props.open_report(e, props.report)}>
      <StatusPieChart red={summary.red} green={summary.green} yellow={summary.yellow} grey={summary.grey} />
      <Card.Content>
        <Card.Header>{props.report.title}</Card.Header>
        <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
      </Card.Content>
    </Card>
  )
}

function Dashboard(props) {
  const tags = [{
    "summary": {
      "red": 15,
      "green": 5,
      "yellow": 0,
      "grey": 1
    },
    "title": "security"
  },
  {
    "summary": {
      "red": 5,
      "green": 13,
      "yellow": 4,
      "grey": 2
    },
    "title": "testability"
  }
];
  const report_cards = props.reports.map((report) =>
                      <ReportCard key={report.report_uuid} report={report} open_report={props.open_report} />);
  const tag_cards = tags.map((tag) =>
                      <ReportCard key={tag.title} report={tag} />);
  const report_cards_per_row = Math.min(Math.max(report_cards.length, 5), 7);
  const tag_cards_per_row = Math.min(Math.max(tag_cards.length, 8), 10);
  return (
    <>
      <Card.Group doubling stackable itemsPerRow={report_cards_per_row}>
            {report_cards}
      </Card.Group>
      <Card.Group doubling stackable itemsPerRow={tag_cards_per_row}>
            {tag_cards}
      </Card.Group>
    </>

  )
}

class Reports extends Component {
  add_report(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/reports/new`, {
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
        <Dashboard reports={this.props.reports} open_report={this.props.open_report} />
        {!this.props.readOnly &&
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
