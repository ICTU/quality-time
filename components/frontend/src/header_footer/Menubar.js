import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Dropdown, Icon, Image, Menu, Message, Portal } from 'semantic-ui-react';
import { Form, Modal, Popup } from '../semantic_ui_react_wrappers';
import FocusLock from 'react-focus-lock';
import { login, logout } from '../api/auth';
import { Avatar } from '../widgets/Avatar';
import { DatePicker } from '../widgets/DatePicker';
import { optionalDatePropType, settingsPropType, uiModePropType } from '../sharedPropTypes';
import { CollapseButton } from './CollapseButton';
import { UIModeMenu } from './UIModeMenu';
import './Menubar.css';
import { ResetSettingsButton } from './ResetSettingsButton';

function Login({ set_user }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    function submit() {
        login(username, password)
            .then(function (json) {
                if (json.ok) {
                    set_user(username, json.email, new Date(Date.parse(json.session_expiration_datetime)))
                } else {
                    setError("credentials");
                }
            })
            .catch(function (_error) {
                setError("connection");
            });
    }

    let messageHeader = "Heads up"
    let messageContent = "Changes you make after you log in, such as adding metrics, changing metric targets, and marking issues as false positive, are logged."
    if (error === "connection") {
        messageHeader = "Connection error"
        messageContent = "Can't reach the server. Please check your connection."
    }
    if (error === "credentials") {
        messageHeader = "Invalid credentials"
        messageContent = "Username and/or password are invalid. Please try again."
    }
    return (
        <Modal trigger={<Button secondary><Icon name='user' />Login</Button>} size='tiny' onClose={() => setError("")} >
            <Modal.Header content='Login' />
            <Modal.Content>
                <Form error={!!error} warning={!error} onSubmit={() => submit()} >
                    <Form.Input autoFocus id='username' name='username' label='Username' onChange={(_event, { value }) => setUsername(value)} />
                    <Form.Input id='password' name='password' type='password' label='Password' onChange={(_event, { value }) => setPassword(value)} />
                    <Message error={!!error} warning={!error} header={messageHeader} content={messageContent} />
                    <Form.Button>Submit</Form.Button>
                </Form>
            </Modal.Content>
        </Modal>
    )
}

function Logout({ user, email, set_user }) {
    const trigger = <><Avatar email={email} /> {user}</>
    return (
        <Dropdown
            trigger={trigger}
            options={[{ key: "logout", text: "Logout", icon: "log out", onClick: () => { logout().then(() => set_user(null)) } }]}
        />
    )
}

export function Menubar({
    atReportsOverview,
    email,
    handleDateChange,
    onDate,
    openReportsOverview,
    panel,
    report_date,
    settings,
    set_user,
    setUIMode,
    uiMode,
    user,
}) {
    const [settingsPanelVisible, setSettingsPanelVisible] = useState(false)
    useEffect(() => {
        function closePanels(event) { if (event.key === "Escape") { setSettingsPanelVisible(false) } }
        window.addEventListener('keydown', closePanels)
        return () => { window.removeEventListener('keydown', closePanels) };
    }, []);

    return (
        <>
            <Menu fluid className="menubar" inverted fixed="top">
                <Menu.Menu position="left">
                    <Popup
                        content="Go to reports overview"
                        disabled={atReportsOverview}
                        trigger={
                            <div onBeforeInput={(event) => { event.preventDefault(); setSettingsPanelVisible(false); openReportsOverview() }} tabIndex={atReportsOverview ? -1 : 0}>
                                <Menu.Item header onClick={atReportsOverview ? null : () => { setSettingsPanelVisible(false); openReportsOverview() }}>
                                    <Image size='mini' src='/favicon.ico' alt="Go home" />
                                    <span style={{ paddingLeft: "6mm", fontSize: "2em" }}>Quality-time</span>
                                </Menu.Item>
                            </div>
                        }
                    />
                    <FocusLock group="settingsPanel" disabled={!settingsPanelVisible} className="center">
                        <div onBeforeInput={(event) => { event.preventDefault(); setSettingsPanelVisible(!settingsPanelVisible) }} tabIndex={0}>
                            <Menu.Item onClick={(event) => { event.stopPropagation(); setSettingsPanelVisible(!settingsPanelVisible) }}>
                                <Icon size='large' name={`caret ${settingsPanelVisible ? "down" : "right"}`} />
                                Settings
                            </Menu.Item>
                        </div>
                    </FocusLock>
                    <Menu.Item>
                        <ResetSettingsButton
                            atReportsOverview={atReportsOverview}
                            handleDateChange={handleDateChange}
                            reportDate={report_date}
                            settings={settings}
                        />
                    </Menu.Item>
                    <Menu.Item>
                        <CollapseButton expandedItems={settings.expandedItems} />
                    </Menu.Item>
                </Menu.Menu>
                <Menu.Menu position='right'>
                    <Popup content="Show the report as it was on the selected date" position="left center" trigger={
                        <Menu.Item>
                            <Form>
                                <DatePicker
                                    isClearable={true}
                                    maxDate={new Date()}
                                    onChange={onDate}
                                    selected={report_date}
                                />
                            </Form>
                        </Menu.Item>
                    } />
                    <Menu.Item>
                        <UIModeMenu setUIMode={setUIMode} uiMode={uiMode} />
                    </Menu.Item>
                    <Menu.Item>
                        {(user !== null) ? <Logout email={email} user={user} set_user={set_user} /> : <Login set_user={set_user} />}
                    </Menu.Item>
                </Menu.Menu>
            </Menu>
            <Portal closeOnTriggerClick={true} open={settingsPanelVisible} onClose={(event) => { event.stopPropagation(); setSettingsPanelVisible(false) }} unmountOnHide>
                <div className="panel">
                    <FocusLock group="settingsPanel">
                        {panel}
                    </FocusLock>
                </div>
            </Portal>
        </>
    )
}
Menubar.propTypes = {
    atReportsOverview: PropTypes.bool,
    email: PropTypes.string,
    handleDateChange: PropTypes.func,
    onDate: PropTypes.func,
    openReportsOverview: PropTypes.func,
    panel: PropTypes.element,
    report_date: optionalDatePropType,
    settings: settingsPropType,
    set_user: PropTypes.func,
    setUIMode: PropTypes.func,
    uiMode: uiModePropType,
    user: PropTypes.string,
}
