import "./Menubar.css"

import { AppBar, Button, Drawer, Stack, Toolbar } from "@mui/material"
import { element, func, string } from "prop-types"
import { useEffect, useState } from "react"
import { Dropdown, Icon } from "semantic-ui-react"

import { login, logout } from "../api/auth"
import { Form, Message, Modal } from "../semantic_ui_react_wrappers"
import { optionalDatePropType, settingsPropType, uiModePropType } from "../sharedPropTypes"
import { Avatar } from "../widgets/Avatar"
import { CollapseButton } from "./buttons/CollapseButton"
import { DatePickerButton } from "./buttons/DatePickerButton"
import { DownloadAsPDFButton } from "./buttons/DownloadAsPDFButton"
import { HomeButton } from "./buttons/HomeButton"
import { ResetSettingsButton } from "./buttons/ResetSettingsButton"
import { SettingsButton } from "./buttons/SettingsButton"
import { UIModeMenu } from "./UIModeMenu"

function Login({ set_user }) {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")

    function submit() {
        login(username, password)
            .then(function (json) {
                if (json.ok) {
                    set_user(username, json.email, new Date(Date.parse(json.session_expiration_datetime)))
                } else {
                    setError("credentials")
                }
                return null
            })
            .catch(function (_error) {
                setError("connection")
            })
    }

    let messageHeader = "Heads up"
    let messageContent =
        "Changes you make after you log in, such as adding metrics, changing metric targets, and marking issues as false positive, are logged."
    if (error === "connection") {
        messageHeader = "Connection error"
        messageContent = "Can't reach the server. Please check your connection."
    }
    if (error === "credentials") {
        messageHeader = "Invalid credentials"
        messageContent = "Username and/or password are invalid. Please try again."
    }
    return (
        <Modal
            trigger={
                <Button color="inherit">
                    <Icon name="user" />
                    Login
                </Button>
            }
            size="tiny"
            onClose={() => setError("")}
        >
            <Modal.Header content="Login" />
            <Modal.Content>
                <Form error={!!error} warning={!error} onSubmit={() => submit()}>
                    <Form.Input
                        autoFocus
                        id="username"
                        name="username"
                        label="Username"
                        onChange={(_event, { value }) => setUsername(value)}
                    />
                    <Form.Input
                        id="password"
                        name="password"
                        type="password"
                        label="Password"
                        onChange={(_event, { value }) => setPassword(value)}
                    />
                    <Message error={!!error} warning={!error} header={messageHeader} content={messageContent} />
                    <Form.Button>Submit</Form.Button>
                </Form>
            </Modal.Content>
        </Modal>
    )
}
Login.propTypes = {
    set_user: func,
}

function Logout({ user, email, set_user }) {
    const trigger = (
        <>
            <Avatar email={email} /> {user}
        </>
    )
    return (
        <Dropdown
            trigger={trigger}
            options={[
                {
                    key: "logout",
                    text: "Logout",
                    icon: "log out",
                    onClick: () => {
                        logout()
                        set_user(null)
                    },
                },
            ]}
        />
    )
}
Logout.propTypes = {
    user: string,
    email: string,
    set_user: func,
}

export function Menubar({
    email,
    handleDateChange,
    onDate,
    openReportsOverview,
    panel,
    report_date,
    report_uuid,
    settings,
    set_user,
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

    const atReportsOverview = report_uuid === ""
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
                            reportDate={report_date}
                            settings={settings}
                        />
                        <CollapseButton expandedItems={settings.expandedItems} />
                        <DownloadAsPDFButton report_uuid={report_uuid} />
                    </Stack>
                    <Stack direction="row" spacing={2}>
                        <DatePickerButton onChange={(date) => onDate(date.$d)} reportDate={report_date} />
                        <UIModeMenu setUIMode={setUIMode} uiMode={uiMode} />
                        {user !== null ? (
                            <Logout email={email} user={user} set_user={set_user} />
                        ) : (
                            <Login set_user={set_user} />
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
    report_date: optionalDatePropType,
    report_uuid: string,
    settings: settingsPropType,
    set_user: func,
    setUIMode: func,
    uiMode: uiModePropType,
    user: string,
}
