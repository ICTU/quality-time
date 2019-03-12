import React, { Component } from 'react';
import { Button, Card, Icon, Segment } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';
import { Subjects } from './Subjects.js';

function SubjectCard(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey;
    return (
        <Card>
            <StatusPieChart red={props.red} green={props.green} yellow={props.yellow} grey={props.grey} />
            <Card.Content>
                <Card.Header>{props.title}</Card.Header>
                <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
            </Card.Content>
        </Card>
    )
}

function Dashboard(props) {
    const cards = Object.entries(props.report.subjects).map(([subject_uuid, subject]) =>
        <SubjectCard key={subject_uuid} title={subject.title}
            red={subject.summary.red} green={subject.summary.green}
            yellow={subject.summary.yellow} grey={subject.summary.grey} />);
    return (
        <Card.Group itemsPerRow={6}>
            {cards}
        </Card.Group>
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
