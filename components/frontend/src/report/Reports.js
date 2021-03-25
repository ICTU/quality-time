import React from 'react';
import { Message, Segment } from 'semantic-ui-react';
import { CardDashboard } from '../dashboard/CardDashboard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { Tag } from '../widgets/Tag';
import { add_report, set_reports_attribute, copy_report } from '../api/report';
import { ReportsTitle } from './ReportsTitle';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton, CopyButton } from '../widgets/Button';
import { report_options } from '../widgets/menu_options';

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
    <MetricSummaryCard key={tag} header={<Tag tag={tag} />} onClick={(e) => props.open_report(e, `tag-${tag}`)} {...counts} />
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
    <div id="dashboard">
      <ReportsTitle
        permissions={props.reports_overview.permissions}
        reload={props.reload}
        subtitle={props.reports_overview.subtitle}
        title={props.reports_overview.title}
      />
      <ReportsDashboard layout={props.reports_overview.layout} {...props} />
      <ReadOnlyOrEditable editableComponent={
        <Segment basic>
          <AddButton item_type={"report"} onClick={() => add_report(props.reload)} />
          <CopyButton item_type={"report"} onClick={() => add_report(props.reload)}
          onChange={(source_report_uuid) => copy_report(source_report_uuid, props.reload)}
          get_options={() => report_options(props.reports)} />
        </Segment>
      }
      />
    </div>
  )
}
