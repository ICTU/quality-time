import React from 'react';
import { Subjects } from './Subjects.js';
import { Card } from 'semantic-ui-react';
import { VictoryPie } from 'victory';

function DashboardSubject(props) {
    const nr_metrics = props.red + props.green + props.yellow;
    return (
        <Card>
            <VictoryPie
                colorScale={["rgb(211,59,55)", "rgb(30,148,78)", "rgb(253,197,54)"]}
                padding={20}
                style={{
                    data: { strokeWidth: 0 }
                }}
                innerRadius={75}
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
                <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
            </Card.Content>
        </Card>
    )
}

function Dashboard(props) {
    const cards = Object.entries(props.report.subjects).map(([subject_uuid, subject]) =>
        <DashboardSubject key={subject_uuid} title={subject.title}
            red={subject.summary.red} green={subject.summary.green}
            yellow={subject.summary.yellow} />);
    return (
        <Card.Group itemsPerRow={6}>
            {cards}
        </Card.Group>
    )
}

function Report(props) {
    return (
        <>
            <Dashboard report={props.report} />
            <Subjects datamodel={props.datamodel} subjects={props.report.subjects}
                report_uuid={props.report.report_uuid}
                nr_new_measurements={props.nr_new_measurements} reload={props.reload}
                search_string={props.search_string} report_date={props.report_date} />
        </>
    )
}

export { Report };
