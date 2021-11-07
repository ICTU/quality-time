import React, { useState } from 'react';
import { Button, Container, Form, Header, Icon, Image, Menu, Message, Modal, Dropdown, Popup } from 'semantic-ui-react';
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
            <Header content='Login' />
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

export function Menubar({ go_home, email, user, set_user, onDate, report_date_string }) {
    return (
        <Menu className="Menubar" fixed='top' inverted>
            <Container fluid>
                <Popup content="Go to reports overview" trigger={
                    <Menu.Item header onClick={() => go_home()} tabIndex={0}>
                        <>
                            <Image size='mini' src='/favicon.ico' alt="Go home" />
                            <span style={{ paddingLeft: "6mm", fontSize: "2em" }}>Quality-time</span>
                        </>
                    </Menu.Item>}
                />
                <Menu.Menu position='right'>
                    <Menu.Item>
                        <DatePicker onDate={onDate} name="report_date_string" value={report_date_string} label="Report date" />
                    </Menu.Item>
                    <Menu.Item>
                        {(user !== null) ? <Logout email={email} user={user} set_user={set_user} /> : <Login set_user={set_user} />}
                    </Menu.Item>
                </Menu.Menu>
            </Container>
        </Menu>
    )
}
