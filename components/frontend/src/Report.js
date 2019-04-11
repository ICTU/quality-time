import React, { Component } from 'react';
import { Button, Card, Icon, Segment } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';
import { Subjects } from './Subjects.js';
import { Tag } from './MetricTag.js';

function MetricSummaryCard(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey;
    return (
        <Card>
            <StatusPieChart red={props.red} green={props.green} yellow={props.yellow} grey={props.grey} />
            <Card.Content>
                <Card.Header>{props.header}</Card.Header>
                <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
            </Card.Content>
        </Card>
    )
}

function Dashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard key={subject_uuid} header={props.report.subjects[subject_uuid].name}
            red={summary.red} green={summary.green} yellow={summary.yellow} grey={summary.grey} />);
    const tag_cards = Object.entries(props.report.summary_by_tag).map(([tag, summary]) =>
        <MetricSummaryCard key={tag} header={<Tag tag={tag}/>}
            red={summary.red} green={summary.green} yellow={summary.yellow} grey={summary.grey} />);
    const subject_cards_per_row = Math.min(Math.max(subject_cards.length, 5), 7);
    const tag_cards_per_row = Math.min(Math.max(tag_cards.length, 8), 10);
    return (
        <>
            <Card.Group doubling stackable itemsPerRow={subject_cards_per_row}>
                {subject_cards}
            </Card.Group>
            <Card.Group itemsPerRow={tag_cards_per_row}>
                {tag_cards}
            </Card.Group>
        </>
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
                <Dashboard report={this.props.report} />
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
