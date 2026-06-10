import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { func } from "prop-types"
import { useContext } from "react"

import { addSourceLocation } from "../api/source_location"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { availabilityMessagePropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { sourceTypeOption } from "../source/SourceType"
import { getSourceLocationName, sourceTypeHasLocation } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddDropdownButton } from "../widgets/buttons/AddDropdownButton"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { InfoMessage } from "../widgets/WarningMessage"
import { sortedSourceLocations, sourcesUsingSourceLocation } from "./report_utils"
import { SourceLocationDetails } from "./SourceLocationDetails"

function sourceTypeOptionsWithLocation(dataModel) {
    // Return menu options for all source types that have source locations
    const sourceTypeKeys = Object.keys(dataModel.sources).filter((sourceTypeKey) =>
        sourceTypeHasLocation(dataModel, sourceTypeKey),
    )
    const options = sourceTypeKeys.map((sourceTypeKey) =>
        sourceTypeOption(sourceTypeKey, dataModel.sources[sourceTypeKey]),
    )
    options.sort((option1, option2) => option1.text.localeCompare(option2.text))
    return options
}

function AddSourceLocationButtonRow({ reload, report }) {
    const dataModel = useContext(DataModelContext)
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingLeft={0} paddingRight={0} paddingTop={2}>
                    <AddDropdownButton
                        itemType="source location"
                        itemSubtypes={sourceTypeOptionsWithLocation(dataModel)}
                        onClick={(subtype) => addSourceLocation(report.report_uuid, subtype, reload)}
                    />
                </ButtonRow>
            }
        />
    )
}
AddSourceLocationButtonRow.propTypes = {
    reload: func,
    report: reportPropType,
}

export function SourceLocations({ fieldWithUrlAvailabilityError, reload, report, settings }) {
    const dataModel = useContext(DataModelContext)
    const sourceLocations = sortedSourceLocations(dataModel, report)
    return (
        <>
            {sourceLocations.length === 0 ? (
                <InfoMessage title="No source locations">
                    No source locations have been configured yet. Source locations contain the location parameters of
                    sources, such as the URL and the credentials, so they can be shared between metrics.
                </InfoMessage>
            ) : (
                <TableContainer>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <UnsortableTableHeaderCell label="Source location" />
                                <UnsortableTableHeaderCell label="Source type" />
                                <UnsortableTableHeaderCell label="URL" />
                                <UnsortableTableHeaderCell
                                    textAlign="right"
                                    label="Number of sources using the source location"
                                />
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {sourceLocations.map(([sourceLocationUuid, sourceLocation]) => (
                                <TableRowWithDetails
                                    details={
                                        <SourceLocationDetails
                                            fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityError}
                                            reload={reload}
                                            report={report}
                                            settings={settings}
                                            sourceLocation={sourceLocation}
                                            sourceLocationUuid={sourceLocationUuid}
                                        />
                                    }
                                    expanded={settings.expandedItems.includes(sourceLocationUuid)}
                                    key={sourceLocationUuid}
                                    onExpand={() => settings.expandedItems.toggle(sourceLocationUuid)}
                                    firstCellContent={getSourceLocationName(sourceLocation, dataModel)}
                                >
                                    <TableCell>
                                        {dataModel.sources[sourceLocation.source_type]?.name ??
                                            sourceLocation.source_type}
                                    </TableCell>
                                    <TableCell>{sourceLocation.url ?? ""}</TableCell>
                                    <TableCell align="right">
                                        {sourcesUsingSourceLocation(report, sourceLocationUuid)}
                                    </TableCell>
                                </TableRowWithDetails>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
            <AddSourceLocationButtonRow reload={reload} report={report} />
        </>
    )
}
SourceLocations.propTypes = {
    fieldWithUrlAvailabilityError: availabilityMessagePropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
