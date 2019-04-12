import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Subjects } from './Subjects.js';
import { Tag } from './MetricTag.js';
import { MetricSummaryCard } from './MetricSummaryCard';
import { CardDashboard } from './CardDashboard';

function ReportDashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard key={subject_uuid} header={props.report.subjects[subject_uuid].name} {...summary} />);
    const tag_cards = Object.entries(props.report.summary_by_tag).map(([tag, summary]) =>
        <MetricSummaryCard key={tag} header={<Tag tag={tag}/>} {...summary} />);
    return (
        <CardDashboard big_cards={subject_cards} small_cards={tag_cards} />
    )
}

class Report extends Component {
    delete_report(event, report) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${report.report_uuid}`, {
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
        return (
            <>
                <ReportDashboard report={this.props.report} />
                <Subjects
                    datamodel={this.props.datamodel}
                    nr_new_measurements={this.props.nr_new_measurements}
                    readOnly={this.props.readOnly}
                    reload={this.props.reload}
                    report={this.props.report}
                    report_date={this.props.report_date}
                    search_string={this.props.search_string}
                />
                {!this.props.readOnly &&
                    <Segment basic>
                        <Button icon negative basic floated='right'
                            onClick={(e) => this.delete_report(e, this.props.report)}>
                            <Icon name='trash' /> Delete report
                        </Button>
                    </Segment>}
            </>
        )
    }
}

export { Report };
