import ChecklistIcon from "@mui/icons-material/Checklist"
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted"
import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import { bool, func, string } from "prop-types"

import { deleteSourceLocation } from "../api/source_location"
import { ChangeLog } from "../changelog/ChangeLog"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import {
    availabilityMessagePropType,
    reportPropType,
    settingsPropType,
    sourceLocationPropType,
} from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { Tabs } from "../widgets/Tabs"
import { sourcesUsingSourceLocation } from "./report_utils"
import { SourceLocationMetrics } from "./SourceLocationMetrics"
import { SourceLocationParameters } from "./SourceLocationParameters"
import { UnusedMetricTypes } from "./UnusedMetricTypes"

function SourceLocationButtonRow({ inUse, reload, sourceLocationUuid }) {
    const deleteButton = (
        <DeleteButton
            disabled={inUse}
            itemType="source location"
            onClick={() => deleteSourceLocation(sourceLocationUuid, reload)}
            popup={
                inUse
                    ? "This source location cannot be deleted because it is used by one or more sources. " +
                      "Remove the source location from the sources that use it first."
                    : "Delete this source location. Careful, this can only be undone by a system administrator!"
            }
        />
    )
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow
                    paddingBottom={1}
                    paddingLeft={0}
                    paddingRight={0}
                    paddingTop={2}
                    rightButton={deleteButton}
                />
            }
        />
    )
}
SourceLocationButtonRow.propTypes = {
    inUse: bool,
    reload: func,
    sourceLocationUuid: string,
}

export function SourceLocationDetails({
    fieldWithUrlAvailabilityError,
    reload,
    report,
    settings,
    sourceLocation,
    sourceLocationUuid,
}) {
    const tabs = [
        { label: "Configuration", icon: <SettingsIcon /> },
        { label: "Metrics using the source location", icon: <ChecklistIcon /> },
        { label: "Unused metric types", icon: <FormatListBulletedIcon /> },
        { label: "Changelog", icon: <HistoryIcon /> },
    ]
    const panes = [
        <SourceLocationParameters
            fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityError}
            key={sourceLocationUuid}
            reload={reload}
            sourceLocation={sourceLocation}
            sourceLocationUuid={sourceLocationUuid}
        />,
        <SourceLocationMetrics key="metrics" report={report} sourceLocationUuid={sourceLocationUuid} />,
        <UnusedMetricTypes key="unused_metric_types" report={report} sourceLocationUuid={sourceLocationUuid} />,
        <ChangeLog key="changelog" sourceLocationUuid={sourceLocationUuid} timestamp={report.timestamp} />,
    ]
    return (
        <>
            <Tabs settings={settings} tabs={tabs} uuid={sourceLocationUuid}>
                {panes}
            </Tabs>
            <SourceLocationButtonRow
                inUse={sourcesUsingSourceLocation(report, sourceLocationUuid) > 0}
                reload={reload}
                sourceLocationUuid={sourceLocationUuid}
            />
        </>
    )
}
SourceLocationDetails.propTypes = {
    fieldWithUrlAvailabilityError: availabilityMessagePropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    sourceLocation: sourceLocationPropType,
    sourceLocationUuid: string,
}
