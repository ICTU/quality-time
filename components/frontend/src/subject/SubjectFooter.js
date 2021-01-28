import { Table } from "semantic-ui-react";
import { add_metric, copy_metric, move_metric } from "../api/metric";
import { ReadOnlyOrEditable } from "../context/ReadOnly";
import { AddButton, CopyButton, MoveButton } from "../widgets/Button";
import { metric_options } from "../widgets/menu_options";

export function SubjectFooter({datamodel, subject, subjectUuid, reload, reports, resetSortColumn}) {
    return (
        <ReadOnlyOrEditable editableComponent={
          <Table.Footer>
            <Table.Row>
              <Table.HeaderCell colSpan='10'>
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
                  get_options={() => metric_options(reports, datamodel, subject.type)}
                />
                <MoveButton
                  item_type="metric"
                  onChange={(source_metric_uuid) => {
                    resetSortColumn()
                    move_metric(source_metric_uuid, subjectUuid, reload);
                  }}
                  get_options={() => metric_options(reports, datamodel, subject.type, subjectUuid)}
                />
              </Table.HeaderCell>
            </Table.Row>
          </Table.Footer>}
        />
      )
} 