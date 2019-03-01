import React, { Component } from 'react';
import { Subjects } from './Subjects.js';
import { Card } from 'semantic-ui-react';
import { VictoryPie } from 'victory';

function DashboardSubject(props) {
    return (
        <Card>
            <VictoryPie
                colorScale={["rgb(211,59,55)", "rgb(30,148,78)", "rgb(253,197,54)"]}
                style={{
                    data: { stroke: "grey", strokeWidth: 0 }
                }}
                labels={() => null}
                animate={{ duration: 2000 }}
                data={[
                    { y: props.red },
                    { y: props.green },
                    { y: props.yellow }
                ]}
            />
            <Card.Content>
                <Card.Header>{props.title}</Card.Header>
            </Card.Content>
        </Card>
    )
}

class Dashboard extends Component {
    constructor(props) {
        super(props);
        this.state = { summary: {} }
    }
    componentDidMount() {
        this.fetch_summary();
    }
    componentDidUpdate(prevProps) {
        if (prevProps.report_date !== this.props.report_date ||
          (prevProps.nr_new_measurements !== 0 && this.props.nr_new_measurements === 0)) {
          this.fetch_summary();
        }
      }
    fetch_summary() {
        let self = this;
        const report_date = this.props.report_date ? this.props.report_date : new Date();
        fetch(`http://localhost:8080/report/${this.props.report.report_uuid}/summary?report_date=${report_date.toISOString()}`)
            .then(function (response) {
                return response.json();
            })
            .then(function (json) {
                self.setState({ summary: json });
            })
    }
    render() {
        const summary = this.state.summary;
        const cards = Object.entries(this.props.report.subjects).map(([subject_uuid, subject]) =>
            <DashboardSubject key={subject_uuid} title={subject.title}
                red={summary[subject_uuid] ? summary[subject_uuid].red : 0}
                green={summary[subject_uuid] ? summary[subject_uuid].green : 0}
                yellow={summary[subject_uuid] ? summary[subject_uuid].yellow : 1} />
        )
        return (
            <Card.Group itemsPerRow={6}>
                {cards}
            </Card.Group>
        )
    }
}

function Report(props) {
    return (
        <>
            <Dashboard report={props.report} report_date={props.report_date}
                nr_new_measurements={props.nr_new_measurements} />
            <Subjects datamodel={props.datamodel} subjects={props.report.subjects}
                report_uuid={props.report.report_uuid}
                nr_new_measurements={props.nr_new_measurements} reload={props.reload}
                search_string={props.search_string} report_date={props.report_date} />
        </>
    )
}

export { Report };
