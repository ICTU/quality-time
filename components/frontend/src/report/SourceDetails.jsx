import ChecklistIcon from "@mui/icons-material/Checklist"
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted"
import SettingsIcon from "@mui/icons-material/Settings"
import { func, string } from "prop-types"

import { reportPropType, settingsPropType, sourcePropType } from "../sharedPropTypes"
import { Tabs } from "../widgets/Tabs"
import { LocationParameters } from "./LocationParameters"
import { SourceMetrics } from "./SourceMetrics"
import { UnusedMetricTypes } from "./UnusedMetricTypes"

export function SourceDetails({ reload, report, settings, source, sourceUuid }) {
    const tabs = [
        { label: "Source configuration", icon: <SettingsIcon /> },
        { label: "Metrics using the source", icon: <ChecklistIcon /> },
        { label: "Unused metric types", icon: <FormatListBulletedIcon /> },
    ]
    const panes = [
        <LocationParameters key={sourceUuid} reload={reload} report={report} source={source} sourceUuid={sourceUuid} />,
        <SourceMetrics key="metrics" report={report} source={source} />,
        <UnusedMetricTypes key="unused_metric_types" report={report} source={source} />,
    ]
    return (
        <Tabs settings={settings} tabs={tabs} uuid={sourceUuid}>
            {panes}
        </Tabs>
    )
}
SourceDetails.propTypes = {
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    source: sourcePropType,
    sourceUuid: string,
}
