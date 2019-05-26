import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { CardDashboard } from '../dashboard/CardDashboard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { Tag } from '../widgets/Tag';
import { add_report } from '../api/report';

function ReportsDashboard(props) {
  var tag_counts = {};
  props.reports.forEach((report) => {
    Object.entries(report.summary_by_tag).forEach(([tag, counts]) => {
      if (Object.keys(tag_counts).indexOf(tag) === -1) {
        tag_counts[tag] = { "red": 0, "green": 0, "yellow": 0, "grey": 0, "white": 0 }
      }
      Object.entries(counts).forEach(([color, color_count]) => { tag_counts[tag][color] += color_count })
    })
  });
  const report_cards = props.reports.map((report) =>
    <MetricSummaryCard key={report.report_uuid} header={report.title}
      onClick={(e) => props.open_report(e, report.report_uuid)} {...report.summary}
    />);
  const tag_cards = Object.entries(tag_counts).map(([tag, counts]) =>
    <MetricSummaryCard key={tag} header={<Tag tag={tag} />} {...counts}
    />);
  return (
    <CardDashboard big_cards={report_cards} small_cards={tag_cards} />
  )
}

export function Reports(props) {
  return (
    <>
      <ReportsDashboard reports={props.reports} open_report={props.open_report} />
      <Segment basic>
        {!props.readOnly &&
          <Button icon primary basic onClick={() => add_report(props.reload)}>
            <Icon name='plus' /> Add report
          </Button>
        }
      </Segment>
    </>
  )
}
