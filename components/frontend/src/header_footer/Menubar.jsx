import "./Menubar.css"

import { AppBar, Drawer, Stack, Toolbar } from "@mui/material"
import { element, func, string } from "prop-types"
import { useEffect, useState } from "react"

import { optionalDatePropType, settingsPropType, uiModePropType } from "../sharedPropTypes"
import { CollapseButton } from "./buttons/CollapseButton"
import { DatePickerButton } from "./buttons/DatePickerButton"
import { DownloadAsPdfButton } from "./buttons/DownloadAsPdfButton"
import { HomeButton } from "./buttons/HomeButton"
import { LoginButton } from "./buttons/LoginButton"
import { ResetSettingsButton } from "./buttons/ResetSettingsButton"
import { SettingsButton } from "./buttons/SettingsButton"
import { UserButton } from "./buttons/UserButton"
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
    const [settingsPanelVisible, setSettingsPanelVisible] = useState(false)
    useEffect(() => {
        function closePanels(event) {
            if (event.key === "Escape") {
                setSettingsPanelVisible(false)
            }
        }
        window.addEventListener("keydown", closePanels)
        return () => {
            window.removeEventListener("keydown", closePanels)
        }
    }, [])

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
                            openReportsOverview={openReportsOverview}
                            setSettingsPanelVisible={setSettingsPanelVisible}
                        />
                        <SettingsButton
                            setSettingsPanelVisible={setSettingsPanelVisible}
                            settingsPanelVisible={settingsPanelVisible}
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
                        <DatePickerButton onChange={(date) => onDate(date.$d)} reportDate={reportDate} />
                        <UIModeMenu setUIMode={setUIMode} uiMode={uiMode} />
                        {user !== null ? (
                            <UserButton email={email} user={user} setUser={setUser} />
                        ) : (
                            <LoginButton setUser={setUser} />
                        )}
                    </Stack>
                </Toolbar>
            </AppBar>
            <Drawer anchor="top" open={settingsPanelVisible} onClose={() => setSettingsPanelVisible(false)}>
                <Toolbar /* Add an empty toolbar to the drawer so the panel is not partly hidden by the appbar. */ />
                {panel}
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
