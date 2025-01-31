import { Box, Stack, Tab, Tabs as MUITabs } from "@mui/material"
import { arrayOf, object } from "prop-types"
import { useId, useState } from "react"

import { childrenPropType } from "../sharedPropTypes"
import { Label } from "./Label"

export function Tabs({ children, tabs }) {
    const tabsId = useId()
    const [tabIndex, setTabIndex] = useState(0)
    return (
        <Stack>
            <MUITabs
                value={tabIndex}
                onChange={(_event, newTabIndex) => setTabIndex(newTabIndex)}
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
                            //sx={{ flex: 1 }}
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
    tabs: arrayOf(object),
}
