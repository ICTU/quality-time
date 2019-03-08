import React, { Component } from 'react';
import { Button, Card, Icon, Segment } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';
import { Subjects } from './Subjects.js';

function SubjectCard(props) {
    const nr_metrics = props.red + props.green + props.yellow;
    return (
        <Card>
            <StatusPieChart red={props.red} green={props.green} yellow={props.yellow} />
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
            yellow={subject.summary.yellow} />);
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
                <Subjects datamodel={this.props.datamodel} subjects={this.props.report.subjects}
                    report_uuid={this.props.report.report_uuid}
                    nr_new_measurements={this.props.nr_new_measurements} reload={this.props.reload}
                    search_string={this.props.search_string} report_date={this.props.report_date}
                    user={this.props.user} />
                {(this.props.user !== null) &&
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
