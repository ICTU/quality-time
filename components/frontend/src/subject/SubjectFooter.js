import { useContext } from "react";
import { Table } from "semantic-ui-react";
import { add_metric, copy_metric, move_metric } from "../api/metric";
import { DataModel } from "../context/DataModel";
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions";
import { AddButton, CopyButton, MoveButton } from "../widgets/Button";
import { metric_options } from "../widgets/menu_options";

export function SubjectFooter({ subject, subjectUuid, reload, reports, resetSortColumn }) {
    const dataModel = useContext(DataModel)
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Table.Footer>
                <Table.Row>
                    <Table.HeaderCell colSpan='11'>
                        <AddButton item_type="metric" onClick={() => {
                            resetSortColumn()
                            add_metric(subjectUuid, reload);
                        }}
                        />
                        <CopyButton
                            item_type="metric"
                            onChange={(source_metric_uuid) => {
                                resetSortColumn()
                                copy_metric(source_metric_uuid, subjectUuid, reload);
                            }}
                            get_options={() => metric_options(reports, dataModel, subject.type)}
                        />
                        <MoveButton
                            item_type="metric"
                            onChange={(source_metric_uuid) => {
                                resetSortColumn()
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