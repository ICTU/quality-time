import React, { useContext } from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { CopyButton, AddButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { useDelayedRender, useURLSearchQuery } from '../utils';
import { DataModel } from '../context/Contexts';

export function Subjects({
        hiddenColumns, 
        tags, 
        toggleHiddenColumn,
        report,
        report_date,
        changed_fields, 
        reload,
        reports,
        history}) {
    const visible = useDelayedRender();
    const dataModel = useContext(DataModel)
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean");
    // eslint-disable-next-line
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array");
    const [subjectTrendTable, setSubjectTrendTable] = useURLSearchQuery(history, "subject_trend_table", "boolean")
    const [trendTableNrDates, setTrendTableNrDates] = useURLSearchQuery(history, "trend_table_nr_dates", "integer", 7);
    const [trendTableInterval, setTrendTableInterval] = useURLSearchQuery(history, "trend_table_interval", "integer", 1);
    const last_index = Object.keys(report.subjects).length - 1;
    return (
        <>
            {Object.keys(report.subjects).map((subject_uuid, index) =>
                visible || index < 3 ?
                    <Subject
                        changed_fields={changed_fields}
                        first_subject={index === 0}
                        hiddenColumns={hiddenColumns}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        last_subject={index === last_index}
                        report={report}
                        report_date={report_date}
                        reports={reports}
                        setHideMetricsNotRequiringAction={(state) => setHideMetricsNotRequiringAction(state)}
                        setSubjectTrendTable={(state) => setSubjectTrendTable(state)}
                        setTrendTableInterval={(interval) => setTrendTableInterval(interval)}
                        setTrendTableNrDates={(nr) => setTrendTableNrDates(nr)}
                        subject_uuid={subject_uuid}
                        subjectTrendTable={subjectTrendTable}
                        tags={tags}
                        toggleHiddenColumn={toggleHiddenColumn}
                        toggleVisibleDetailsTab={(...tabs) => toggleVisibleDetailsTab(...tabs)}
                        trendTableInterval={trendTableInterval}
                        trendTableNrDates={trendTableNrDates}
                        visibleDetailsTabs={visibleDetailsTabs}
                        reload={reload}
                    /> : null
            )}
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Segment basic>
                    <AddButton item_type="subject" onClick={() => add_subject(report.report_uuid, reload)} />
                    <CopyButton
                        item_type="subject"
                        onChange={(source_subject_uuid) => copy_subject(source_subject_uuid, report.report_uuid, reload)}
                        get_options={() => subject_options(reports, dataModel)}
                    />
                    <MoveButton
                        item_type="subject"
                        onChange={(source_subject_uuid) => move_subject(source_subject_uuid, report.report_uuid, reload)}
                        get_options={() => subject_options(reports, dataModel, report.report_uuid)}
                    />
                </Segment>}
            />
        </>
    )
}
