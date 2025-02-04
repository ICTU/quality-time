import { metricsToHidePropType, metricsToHideURLSearchQueryPropType, settingsPropType } from "../../sharedPropTypes"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function VisibleMetricMenu({ settings }) {
    const metricMenuItemProps = { metricsToHide: settings.metricsToHide }
    return (
        <SettingsMenu title="Visible metrics">
            <VisibleMetricMenuItem hide="none" {...metricMenuItemProps} />
            <VisibleMetricMenuItem hide="no_action_required" {...metricMenuItemProps} />
            <VisibleMetricMenuItem hide="no_issues" {...metricMenuItemProps} />
            <VisibleMetricMenuItem hide="all" {...metricMenuItemProps} />
        </SettingsMenu>
    )
}
VisibleMetricMenu.propTypes = {
    settings: settingsPropType,
}

function VisibleMetricMenuItem({ hide, metricsToHide }) {
    return (
        <SettingsMenuItem active={metricsToHide.equals(hide)} onClick={metricsToHide.set} onClickData={hide}>
            {
                {
                    none: "All metrics",
                    no_action_required: "Metrics requiring action",
                    no_issues: "Metrics with issues",
                    all: "No metrics",
                }[hide]
            }
        </SettingsMenuItem>
    )
}
VisibleMetricMenuItem.propTypes = {
    hide: metricsToHidePropType,
    metricsToHide: metricsToHideURLSearchQueryPropType,
}
