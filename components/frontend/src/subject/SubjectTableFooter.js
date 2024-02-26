import { useContext } from "react";
import { func, string } from 'prop-types';
import { Table } from "semantic-ui-react";
import { add_metric, copy_metric, move_metric } from "../api/metric";
import { DataModel } from "../context/DataModel";
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions";
import { AddDropdownButton, CopyButton, MoveButton } from "../widgets/Button";
import { metric_options } from "../widgets/menu_options";
import { metricTypeOptions } from "../metric/MetricType";
import { reportsPropType, subjectPropType } from '../sharedPropTypes';

export function SubjectTableFooter({ subject, subjectUuid, reload, reports, stopFilteringAndSorting }) {
    const dataModel = useContext(DataModel)
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Table.Footer>
                <Table.Row>
                    <Table.HeaderCell colSpan='99'>
                        <AddDropdownButton
                            itemType="metric"
                            itemSubtypes={metricTypeOptions(dataModel, subject.type)}
                            onClick={(subtype) => {
                                stopFilteringAndSorting()
                                add_metric(subjectUuid, subtype, reload);
                            }}
                        />
                        <CopyButton
                            itemType="metric"
                            onChange={(source_metric_uuid) => {
                                stopFilteringAndSorting()
                                copy_metric(source_metric_uuid, subjectUuid, reload);
                            }}
                            get_options={() => metric_options(reports, dataModel, subject.type)}
                        />
                        <MoveButton
                            itemType="metric"
                            onChange={(source_metric_uuid) => {
                                stopFilteringAndSorting()
                                move_metric(source_metric_uuid, subjectUuid, reload);
                            }}
                            get_options={() => metric_options(reports, dataModel, subject.type, subjectUuid)}
                        />
                    </Table.HeaderCell>
                </Table.Row>
            </Table.Footer>}
        />
    )
}
SubjectTableFooter.propTypes = {
    subject: subjectPropType,
    subjectUuid: string,
    reload: func,
    reports: reportsPropType,
    stopFilteringAndSorting: func,
}
