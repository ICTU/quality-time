import { TableCell, TableFooter, TableRow } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { addMetric, copyMetric, moveMetric } from "../api/metric"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import {
    allMetricTypeOptions,
    metricTypeOptions,
    usedMetricTypesInReport,
    usedMetricTypesInSubject,
} from "../metric/MetricTypeSelector"
import { reportPropType, reportsPropType, subjectPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddItemByTypeButton } from "../widgets/buttons/AddItemByTypeButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { MoveButton } from "../widgets/buttons/MoveButton"
import { metricOptions } from "../widgets/menu_options"

function SubjectTableFooterButtonRow({ subject, subjectUuid, reload, report, reports, stopFilteringAndSorting }) {
    const dataModel = useContext(DataModelContext)
    return (
        <TableRow>
            <TableCell colSpan="99">
                <ButtonRow paddingLeft={0} paddingRight={0}>
                    <AddItemByTypeButton
                        allItemSubtypes={allMetricTypeOptions(dataModel)}
                        itemType="metric"
                        itemSubtypes={metricTypeOptions(dataModel, subject.type)}
                        onClick={(subtype) => {
                            stopFilteringAndSorting()
                            addMetric(subjectUuid, subtype, reload)
                        }}
                        usedItemSubtypeKeysInReport={usedMetricTypesInReport(report)}
                        usedItemSubtypeKeysInSubject={usedMetricTypesInSubject(subject)}
                    />
                    <CopyButton
                        itemType="metric"
                        onChange={(metricUuid) => {
                            stopFilteringAndSorting()
                            copyMetric(metricUuid, subjectUuid, reload)
                        }}
                        getOptions={() => metricOptions(reports, dataModel, subject.type)}
                    />
                    <MoveButton
                        itemType="metric"
                        onChange={(metricUuid) => {
                            stopFilteringAndSorting()
                            moveMetric(metricUuid, subjectUuid, reload)
                        }}
                        getOptions={() => metricOptions(reports, dataModel, subject.type, subjectUuid)}
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
    report: reportPropType,
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
