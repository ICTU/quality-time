import React, { Component } from 'react';
import { Subjects } from '../subject/Subjects';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { ReportTitle } from './ReportTitle'

function ReportDashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard
            key={subject_uuid} header={props.report.subjects[subject_uuid].name}
            onClick={(event) => props.onClick(event, subject_uuid)} {...summary} />);
    const tag_cards = Object.entries(props.report.summary_by_tag).map(([tag, summary]) =>
        <MetricSummaryCard key={tag} header={<Tag tag={tag}/>} {...summary} />);
    return (
        <CardDashboard big_cards={subject_cards} small_cards={tag_cards} />
    )
}

class Report extends Component {
    delete_report(event) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}`, {
            method: 'delete',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then(
            () => self.props.go_home()
        );
    }
    set_report_attribute(key, value) {
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/${key}`, {
            method: 'post',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ [key]: value })
        }).then(
            () => self.props.reload()
        )
    }
    navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, -65);  // Correct for menu bar
    }
    render() {
        return (
            <>
                <ReportTitle
                    report={this.props.report}
                    readOnly={this.props.readOnly}
                    delete_report={(e) => this.delete_report(e)}
                    set_report_attribute={(k, v) => this.set_report_attribute(k, v)}
                />
                <ReportDashboard report={this.props.report} onClick={(e, s) => this.navigate_to_subject(e, s)} />
                <Subjects
                    datamodel={this.props.datamodel}
                    nr_new_measurements={this.props.nr_new_measurements}
                    readOnly={this.props.readOnly}
                    reload={this.props.reload}
                    report={this.props.report}
                    report_date={this.props.report_date}
                    search_string={this.props.search_string}
                />
            </>
        )
    }
}

export { Report };
