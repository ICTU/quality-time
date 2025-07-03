import "./Menubar.css"

import { AppBar, Drawer, Stack, Toolbar } from "@mui/material"
import { element, func, string } from "prop-types"
import { useState } from "react"

import { optionalDatePropType, settingsPropType, uiModePropType } from "../sharedPropTypes"
import { CollapseButton } from "./buttons/CollapseButton"
import { DownloadAsPdfButton } from "./buttons/DownloadAsPdfButton"
import { HomeButton } from "./buttons/HomeButton"
import { LoginButton } from "./buttons/LoginButton"
import { ReportPeriodButton } from "./buttons/ReportPeriodButton"
import { ResetSettingsButton } from "./buttons/ResetSettingsButton"
import { SettingsButton } from "./buttons/SettingsButton"
import { UserButton } from "./buttons/UserButton"
import { ReportPeriodPanel } from "./ReportPeriodPanel"
import { UIModeMenu } from "./UIModeMenu"

export function Menubar({
    email,
    handleDateChange,
    onDate,
    openReportsOverview,
    panel,
    reportDate,
    reportUuid,
    settings,
    setUser,
    setUIMode,
    uiMode,
    user,
}) {
    // Keep track of the visible panel in the drawer: visibleSettingsPanel == "settings" if the drawer is open with the
    // settings panel in it, "reportperiod"` if the drawer is open with the report period panel in it, and an empty
    // string if the drawer is closed:
    const [visibleSettingsPanel, setVisibleSettingsPanel] = useState("")
    const atReportsOverview = reportUuid === ""
    return (
        <>
            <AppBar
                position="fixed"
                sx={{
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                }} // Make sure the app bar is above the drawer for the settings
            >
                <Toolbar>
                    <Stack direction="row" spacing={2} sx={{ flexGrow: 1 }}>
                        <HomeButton
                            atReportsOverview={atReportsOverview}
                            openReportsOverview={() => {
                                setVisibleSettingsPanel("")
                                openReportsOverview()
                            }}
                        />
                        <SettingsButton
                            isSettingsPanelVisible={visibleSettingsPanel === "settings"} // Note the button only needs a boolean
                            setIsSettingsPanelVisible={(visible) => setVisibleSettingsPanel(visible ? "settings" : "")}
                        />
                        <ResetSettingsButton
                            atReportsOverview={atReportsOverview}
                            handleDateChange={handleDateChange}
                            reportDate={reportDate}
                            settings={settings}
                        />
                        <CollapseButton expandedItems={settings.expandedItems} />
                        <DownloadAsPdfButton reportUuid={reportUuid} />
                    </Stack>
                    <Stack direction="row" spacing={2}>
                        <ReportPeriodButton
                            isSettingsPanelVisible={visibleSettingsPanel === "reportperiod"}
                            reportDate={reportDate}
                            setIsSettingsPanelVisible={(visible) =>
                                setVisibleSettingsPanel(visible ? "reportperiod" : "")
                            }
                        />
                        <UIModeMenu setUIMode={setUIMode} uiMode={uiMode} />
                        {user === null ? (
                            <LoginButton setUser={setUser} />
                        ) : (
                            <UserButton email={email} user={user} setUser={setUser} />
                        )}
                    </Stack>
                </Toolbar>
            </AppBar>
            <Drawer anchor="top" open={visibleSettingsPanel} onClose={() => setVisibleSettingsPanel("")}>
                <Toolbar /* Add an empty toolbar to the drawer so the panel is not partly hidden by the appbar. */ />
                {visibleSettingsPanel === "settings" ? (
                    panel
                ) : (
                    <ReportPeriodPanel onChange={onDate} reportDate={reportDate} settings={settings} />
                )}
            </Drawer>
        </>
    )
}
Menubar.propTypes = {
    email: string,
    handleDateChange: func,
    onDate: func,
    openReportsOverview: func,
    panel: element,
    reportDate: optionalDatePropType,
    reportUuid: string,
    settings: settingsPropType,
    setUser: func,
    setUIMode: func,
    uiMode: uiModePropType,
    user: string,
}
