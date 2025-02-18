import { TableCell, TableFooter, TableRow } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { add_metric, copy_metric, move_metric } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { allMetricTypeOptions, metricTypeOptions, usedMetricTypes } from "../metric/MetricType"
import { reportsPropType, subjectPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddDropdownButton } from "../widgets/buttons/AddDropdownButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { MoveButton } from "../widgets/buttons/MoveButton"
import { metric_options } from "../widgets/menu_options"

function SubjectTableFooterButtonRow({ subject, subjectUuid, reload, reports, stopFilteringAndSorting }) {
    const dataModel = useContext(DataModel)
    return (
        <TableRow>
            <TableCell colSpan="99">
                <ButtonRow paddingLeft={0} paddingRight={0}>
                    <AddDropdownButton
                        allItemSubtypes={allMetricTypeOptions(dataModel)}
                        itemType="metric"
                        itemSubtypes={metricTypeOptions(dataModel, subject.type)}
                        onClick={(subtype) => {
                            stopFilteringAndSorting()
                            add_metric(subjectUuid, subtype, reload)
                        }}
                        usedItemSubtypeKeys={usedMetricTypes(subject)}
                    />
                    <CopyButton
                        itemType="metric"
                        onChange={(source_metric_uuid) => {
                            stopFilteringAndSorting()
                            copy_metric(source_metric_uuid, subjectUuid, reload)
                        }}
                        get_options={() => metric_options(reports, dataModel, subject.type)}
                    />
                    <MoveButton
                        itemType="metric"
                        onChange={(source_metric_uuid) => {
                            stopFilteringAndSorting()
                            move_metric(source_metric_uuid, subjectUuid, reload)
                        }}
                        get_options={() => metric_options(reports, dataModel, subject.type, subjectUuid)}
                    />
                </ButtonRow>
            </TableCell>
        </TableRow>
    )
}
SubjectTableFooterButtonRow.propTypes = {
    subject: subjectPropType,
    subjectUuid: string,
    reload: func,
    reports: reportsPropType,
    stopFilteringAndSorting: func,
}

export function SubjectTableFooter(props) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <TableFooter>
                    <SubjectTableFooterButtonRow {...props} />
                </TableFooter>
            }
        />
    )
}
