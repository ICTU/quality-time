import React from 'react';
import { Message, Segment } from 'semantic-ui-react';
import { CardDashboard } from '../dashboard/CardDashboard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { Tag } from '../widgets/Tag';
import { add_report, set_reports_attribute } from '../api/report';
import { ReportsTitle } from './ReportsTitle';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton } from '../widgets/Button';

function ReportsDashboard(props) {
  var tag_counts = {};
  props.reports.forEach((report) => {
    Object.entries(report.summary_by_tag).forEach(([tag, counts]) => {
      if (!Object.keys(tag_counts).includes(tag)) {
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
    <MetricSummaryCard key={tag} header={<Tag tag={tag} />} onClick={(e) => props.open_tag_report(e, tag)} {...counts} />
  );
  return (
    <CardDashboard
      cards={report_cards.concat(tag_cards)}
      initial_layout={props.layout || []}
      save_layout={function (layout) { set_reports_attribute("layout", layout, props.reload) }}
    />
  )
}

export function Reports(props) {
  if (props.reports.length === 0 && props.report_date !== null) {
    return (
      <Message warning size='huge'>
        <Message.Header>
          {`Sorry, no reports existed at ${props.report_date}`}
        </Message.Header>
      </Message>
    )
  }
  return (
    <>
      <ReportsTitle
        reload={props.reload}
        subtitle={props.reports_overview.subtitle}
        title={props.reports_overview.title}
      />
      <ReportsDashboard
        layout={props.reports_overview.layout}
        open_report={props.open_report}
        open_tag_report={props.open_tag_report}
        reload={props.reload}
        reports={props.reports}
      />
      <ReadOnlyOrEditable editableComponent={
        <Segment basic>
          <AddButton item_type={"report"} onClick={() => add_report(props.reload)} />
        </Segment>
      }
      />
    </>
  )
}
