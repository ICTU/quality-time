import React, { useEffect, useState } from 'react';
import { Button, Dropdown, Icon, Image, Menu, Message, Portal } from 'semantic-ui-react';
import { Form, Modal, Popup } from '../semantic_ui_react_wrappers';
import FocusLock from 'react-focus-lock';
import { login, logout } from '../api/auth';
import { DatePicker } from '../widgets/DatePicker';
import { Avatar } from '../widgets/Avatar';
import './Menubar.css';

function Login({ set_user }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [login_error, setLoginError] = useState(false);

    function submit() {
        login(username, password)
            .then(function (json) {
                if (json.ok) {
                    set_user(username, json.email, new Date(Date.parse(json.session_expiration_datetime)))
                } else {
                    setLoginError(true);
                }
            })
            .catch(function (error) {
                setLoginError(true);
            });
    }

    return (
        <Modal trigger={<Button secondary><Icon name='user' />Login</Button>} size='tiny' onClose={() => setLoginError(false)} >
            <Modal.Header content='Login' />
            <Modal.Content>
                <Form error={login_error} warning={!login_error} onSubmit={() => submit()} >
                    <Form.Input autoFocus label='Username' name='username' onChange={(event, { value }) => setUsername(value)} />
                    <Form.Input type='password' label='Password' name='password' onChange={(event, { value }) => setPassword(value)} />
                    <Message error header='Invalid credentials' content='Username and/or password are invalid. Please try again.' />
                    <Message warning header='Heads up' content='Changes you make after you log in, such as adding metrics, changing metric targets, and marking issues as false positive, are logged.' />
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
    current_report,
    email,
    go_home,
    onDate,
    panel,
    report_date_string,
    set_user,
    user,
}) {
    const [panelVisible, setPanelVisible] = useState(false)
    useEffect(() => {
        function closePanel(event) { if (event.key === "Escape") { setPanelVisible(false) } }
        window.addEventListener('keydown', closePanel)
        return () => { window.removeEventListener('keydown', closePanel) };
    }, []);

    return (
        <>
            <Menu fluid className="menubar" inverted fixed="top">
                <Menu.Menu position="left">
                    <Popup
                        content="Go to reports overview"
                        disabled={!current_report}
                        trigger={
                            <div onKeyPress={(event) => { event.preventDefault(); setPanelVisible(false); go_home() }} tabIndex={current_report ? 0 : -1}>
                                <Menu.Item header onClick={current_report ? () => { setPanelVisible(false); go_home() } : null}>
                                    <Image size='mini' src='/favicon.ico' alt="Go home" />
                                    <span style={{ paddingLeft: "6mm", fontSize: "2em" }}>Quality-time</span>
                                </Menu.Item>
                            </div>
                        }
                    />
                    <FocusLock group="panel" disabled={!panelVisible} className="center">
                        <div onKeyPress={(event) => { event.preventDefault(); setPanelVisible(!panelVisible) }} tabIndex={0}>
                            <Menu.Item onClick={(event) => { event.stopPropagation(); setPanelVisible(!panelVisible) }}>
                                <Icon size='large' name={`caret ${panelVisible ? "down" : "right"}`} />
                                Settings
                            </Menu.Item>
                        </div>
                    </FocusLock>
                </Menu.Menu>
                <Menu.Menu position='right'>
                    <Popup content="Show the report as it was on the selected date" position="left center" trigger={
                        <Menu.Item>
                            <DatePicker onDate={onDate} name="report_date_string" value={report_date_string} label="Report date" />
                        </Menu.Item>}
                    />
                    <Menu.Item>
                        {(user !== null) ? <Logout email={email} user={user} set_user={set_user} /> : <Login set_user={set_user} />}
                    </Menu.Item>
                </Menu.Menu>
            </Menu>
            <Portal closeOnTriggerClick={true} open={panelVisible} onClose={(event) => { event.stopPropagation(); setPanelVisible(false) }} unmountOnHide>
                <div className="panel">
                    <FocusLock group="panel">
                        {panel}
                    </FocusLock>
                </div>
            </Portal>
        </>
    )
}
