import { Box, Stack, Tab, Tabs as MUITabs } from "@mui/material"
import { arrayOf, object, string } from "prop-types"
import { useId } from "react"

import { childrenPropType, settingsPropType } from "../sharedPropTypes"
import { Label } from "./Label"

export function Tabs({ children, settings, tabs, uuid }) {
    const tabsId = useId()
    const tabIndex = settings.expandedItems.getItem(uuid)
    return (
        <Stack>
            <MUITabs
                value={tabIndex}
                onChange={(_event, newTabIndex) => settings.expandedItems.setItem(uuid, newTabIndex)}
                scrollButtons="auto"
                sx={{ marginBottom: 1, maxWidth: "95vw" }}
                variant="scrollable"
            >
                {tabs.map((tab, index) => {
                    let tabLabel = tab.label
                    if (tab.error || tab.warning) {
                        const color = tab.error ? "error" : "warning"
                        tabLabel = <Label color={color}>{tab.label}</Label>
                    }
                    return (
                        <Tab
                            id={`tab-${tabsId}-${index}`}
                            icon={tab.icon || tab.image}
                            key={tab.label}
                            label={tabLabel}
                        />
                    )
                })}
            </MUITabs>
            <Box
                aria-labelledby={`tab-${tabsId}-${tabIndex}`}
                id={`tabpanel-${tabsId}-${tabIndex}`}
                sx={{ border: 1, padding: 1, borderColor: "divider" }}
                role="tabpanel"
            >
                {children[tabIndex]}
            </Box>
        </Stack>
    )
}
Tabs.propTypes = {
    children: childrenPropType,
    settings: settingsPropType,
    tabs: arrayOf(object),
    uuid: string,
}
