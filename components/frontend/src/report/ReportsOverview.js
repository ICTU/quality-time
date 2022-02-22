import React from 'react';
import { Message } from 'semantic-ui-react';
import { CardDashboard } from '../dashboard/CardDashboard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { add_report, set_reports_attribute, copy_report } from '../api/report';
import { ReportsOverviewTitle } from './ReportsOverviewTitle';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { AddButton, CopyButton } from '../widgets/Button';
import { Segment } from '../semantic_ui_react_wrappers/Segment';
import { report_options } from '../widgets/menu_options';

function ReportsDashboard({ reports, open_report, layout, reload }) {
    var tag_counts = {};
    reports.forEach((report) => {
        Object.entries(report.summary_by_tag).forEach(([tag, counts]) => {
            if (!Object.keys(tag_counts).includes(tag)) {
                tag_counts[tag] = { "red": 0, "green": 0, "yellow": 0, "grey": 0, "white": 0 }
            }
            Object.entries(counts).forEach(([color, color_count]) => { tag_counts[tag][color] += color_count })
        })
    });
    const report_cards = reports.map((report) =>
        <MetricSummaryCard key={report.report_uuid} header={report.title}
            onClick={(e) => open_report(e, report.report_uuid)} {...report.summary}
        />);
    const tag_cards = Object.entries(tag_counts).map(([tag, counts]) =>
        <MetricSummaryCard key={tag} header={<Tag tag={tag} />} onClick={(e) => open_report(e, `tag-${tag}`)} {...counts} />
    );
    return (
        <CardDashboard
            cards={report_cards.concat(tag_cards)}
            initial_layout={layout || []}
            save_layout={function (new_layout) { set_reports_attribute("layout", new_layout, reload) }}
        />
    )
}

export function ReportsOverview({ reports, open_report, report_date, reports_overview, reload }) {
    if (reports.length === 0 && report_date !== null) {
        return (
            <Message warning size='huge'>
                <Message.Header>
                    {`Sorry, no reports existed at ${report_date}`}
                </Message.Header>
            </Message>
        )
    }
    return (
        <div id="dashboard">
            <ReportsOverviewTitle reports_overview={reports_overview} reload={reload} />
            <CommentSegment comment={reports_overview.comment} />
            <ReportsDashboard reports={reports} open_report={open_report} layout={reports_overview.layout} reload={reload} />
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Segment basic>
                    <AddButton item_type={"report"} onClick={() => add_report(reload)} />
                    <CopyButton item_type={"report"} onClick={() => add_report(reload)}
                        onChange={(source_report_uuid) => copy_report(source_report_uuid, reload)}
                        get_options={() => report_options(reports)} />
                </Segment>
            }
            />
        </div>
    )
}
