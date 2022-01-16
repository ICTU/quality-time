import React, { useContext } from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { CopyButton, AddButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { useDelayedRender, useURLSearchQuery } from '../utils';

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
    const [sortColumn, setSortColumn] = useURLSearchQuery(history, "sort_column", "string", null)
    const [sortDirection, setSortDirection] = useURLSearchQuery(history, "sort_direction", "string", "ascending")
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean", false);
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array");
    const [nrDates, setNrDates] = useURLSearchQuery(history, "nr_dates", "integer", 1);
    const [dateInterval, setDateInterval] = useURLSearchQuery(history, "date_interval", "integer", 7);
    const last_index = Object.keys(report.subjects).length - 1;

    function handleSort(column) {
        if (column === null) {
            setSortColumn(null)  // Stop sorting
            return
        }
        if (sortColumn === column) {
            if (sortDirection === 'descending') {
                setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
        } else {
            setSortColumn(column)
        }
    }

    return (
        <>
            {Object.keys(report.subjects).map((subject_uuid, index) =>
                visible || index < 3 ?
                    <Subject
                        changed_fields={changed_fields}
                        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                        first_subject={index === 0}
                        handleSort={(column) => handleSort(column)}
                        hiddenColumns={hiddenColumns}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        key={subject_uuid}
                        last_subject={index === last_index}
                        report={report}
                        report_date={report_date}
                        reports={reports}
                        setHideMetricsNotRequiringAction={(state) => setHideMetricsNotRequiringAction(state)}
                        setDateInterval={(interval) => setDateInterval(interval)}
                        setNrDates={(nr) => setNrDates(nr)}
                        sortColumn={sortColumn}
                        sortDirection={sortDirection}
                        subject_uuid={subject_uuid}
                        tags={tags}
                        toggleHiddenColumn={toggleHiddenColumn}
                        toggleVisibleDetailsTab={(...tabs) => toggleVisibleDetailsTab(...tabs)}
                        dateInterval={dateInterval}
                        nrDates={nrDates}
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
