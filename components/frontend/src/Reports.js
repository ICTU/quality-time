import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';
import { Tag } from './MetricTag';

function ReportsDashboard(props) {
  var tag_counts = {};
  props.reports.forEach((report) => {
    Object.entries(report.summary_by_tag).forEach(([tag, counts]) => {
      if (Object.keys(tag_counts).indexOf(tag) === -1) {
        tag_counts[tag] = {"red": 0, "green": 0, "yellow": 0, "grey": 0, "white": 0}
      }
      Object.entries(counts).forEach(([color, color_count]) => {tag_counts[tag][color] += color_count})
    })
  });
  const report_cards = props.reports.map((report) =>
    <MetricSummaryCard key={report.report_uuid} header={report.title}
      onClick={(e) => props.open_report(e, report.report_uuid)} {...report.summary}
    />);
  const tag_cards = Object.entries(tag_counts).map(([tag, counts]) =>
    <MetricSummaryCard key={tag} header={<Tag tag={tag}/>} {...counts}
    />);
  return (
    <CardDashboard big_cards={report_cards} small_cards={tag_cards} />
  )
}

class Reports extends Component {
  add_report(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/new`, {
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
        <ReportsDashboard reports={this.props.reports} open_report={this.props.open_report} />
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
