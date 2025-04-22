import { Box } from "@mui/material"
import { func, number, string } from "prop-types"
import { useContext } from "react"

import { addSource, copySource, moveSource } from "../api/source"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import {
    measurementPropType,
    measurementSourcePropType,
    metricPropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { pluralize } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddDropdownButton } from "../widgets/buttons/AddDropdownButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { MoveButton } from "../widgets/buttons/MoveButton"
import { sourceOptions } from "../widgets/menu_options"
import { showMessage } from "../widgets/toast"
import { InfoMessage } from "../widgets/WarningMessage"
import { Source } from "./Source"
import { sourceTypeOptions } from "./SourceType"

function ButtonSegment({ metric, metricUuid, reload, reports }) {
    const dataModel = useContext(DataModel)
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingLeft={0} paddingRight={0} paddingTop={2}>
                    <AddDropdownButton
                        itemType="source"
                        itemSubtypes={sourceTypeOptions(dataModel, metric.type)}
                        onClick={(subtype) => addSource(metricUuid, subtype, reload)}
                    />
                    <CopyButton
                        itemType="source"
                        onChange={(sourceUuid) => copySource(sourceUuid, metricUuid, reload)}
                        getOptions={() => sourceOptions(reports, dataModel, metric.type)}
                    />
                    <MoveButton
                        itemType="source"
                        onChange={(sourceUuid) => moveSource(sourceUuid, metricUuid, reload)}
                        getOptions={() => sourceOptions(reports, dataModel, metric.type, metricUuid)}
                    />
                </ButtonRow>
            }
        />
    )
}
ButtonSegment.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    reports: reportsPropType,
}

function SourceSegment({
    changedFields,
    index,
    lastIndex,
    measurementSource,
    metric,
    reload,
    report,
    settings,
    sourceUuid,
}) {
    return (
        <Box id={sourceUuid} sx={{ border: 1, borderColor: "divider", padding: "8px" }}>
            <Source
                firstSource={index === 0}
                lastSource={index === lastIndex}
                metric={metric}
                measurementSource={measurementSource}
                reload={reload}
                report={report}
                settings={settings}
                sourceUuid={sourceUuid}
                changedFields={changedFields}
            />
        </Box>
    )
}
SourceSegment.propTypes = {
    changedFields: stringsPropType,
    index: number,
    lastIndex: number,
    measurementSource: measurementSourcePropType,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    sourceUuid: string,
}

export function reloadAfterMassEditSource(json, reload) {
    const nrSources = json.nr_sources_mass_edited
    if (nrSources > 0) {
        showMessage("info", `Changed ${nrSources} ${pluralize("source", nrSources)}`)
    }
    reload(json)
}

export function Sources({ reports, report, metric, metricUuid, measurement, changedFields, reload, settings }) {
    const dataModel = useContext(DataModel)
    const measurementSources = measurement?.sources ?? []
    const sourceUuids = Object.keys(metric.sources).filter((sourceUuid) =>
        Object.keys(dataModel.sources).includes(metric.sources[sourceUuid].type),
    )
    const lastIndex = sourceUuids.length - 1
    const sourceSegments = sourceUuids.map((sourceUuid, index) => {
        return (
            <SourceSegment
                key={sourceUuid}
                metric={metric}
                report={report}
                sourceUuid={sourceUuid}
                index={index}
                lastIndex={lastIndex}
                measurementSource={measurementSources.find((source) => source.source_uuid === sourceUuid)}
                changedFields={changedFields}
                reload={(json) => reloadAfterMassEditSource(json, reload)}
                settings={settings}
            />
        )
    })
    return (
        <>
            {sourceSegments.length === 0 ? (
                <InfoMessage title="No sources">No sources have been configured yet.</InfoMessage>
            ) : (
                sourceSegments
            )}
            <ButtonSegment reports={reports} metricUuid={metricUuid} metric={metric} reload={reload} />
        </>
    )
}
Sources.propTypes = {
    changedFields: stringsPropType,
    reports: reportsPropType,
    report: reportPropType,
    metric: metricPropType,
    metricUuid: string,
    measurement: measurementPropType,
    reload: func,
    settings: settingsPropType,
}
