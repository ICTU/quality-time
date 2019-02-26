import React from 'react';
import { Subjects } from './Subjects.js';

function Report(props) {
    return (
        <Subjects datamodel={props.datamodel} subjects={props.report.subjects}
            report_uuid={props.report.report_uuid}
            nr_new_measurements={props.nr_new_measurements} reload={props.reload}
            search_string={props.search_string} report_date={props.report_date} />
    )
}

export { Report };
