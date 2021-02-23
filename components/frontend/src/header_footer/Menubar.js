import React, { useState } from 'react';
import { Button, Container, Form, Header, Icon, Image, Input, Menu, Message, Modal, Dropdown, Popup } from 'semantic-ui-react';
import { login, logout } from '../api/auth';
import { DatePicker } from '../widgets/DatePicker';
import { Avatar } from '../widgets/Avatar';
import './Menubar.css';

function Login(props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [login_error, setLoginError] = useState(false);

  function submit() {
    login(username, password)
      .then(function (json) {
        if (json.ok) {
          props.set_user(username, json.email, new Date(Date.parse(json.session_expiration_datetime)))
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

function Logout(props) {
  const trigger = <><Avatar email={props.email} /> {props.user}</>
  return (
    <Dropdown
      trigger={trigger}
      options={[{ key: "logout", text: "Logout", icon: "log out", onClick: () => {logout().then(() => props.set_user(null))} }]}
    />
  )
}

function go_dashboard(event) {
  event.preventDefault();
  const dashboard = document.getElementById("dashboard");
  if (dashboard) {
    dashboard.scrollIntoView();
    window.scrollBy(0, -65);  // Correct for menu bar
  }
}

export function Menubar(props) {
  return (
    <Menu className="Menubar" fixed='top' inverted>
      <Container fluid>
        <Popup content="Go to reports overview" trigger={
          <Menu.Item header onClick={() => props.go_home()} tabIndex={0}>
            <>
              <Image size='mini' src='/favicon.ico' alt="Go home" />
              <span style={{ paddingLeft: "6mm", fontSize: "2em" }}>Quality-time</span>
            </>
          </Menu.Item>}
        />
        <Popup content="Scroll to dashboard" trigger={
          <Menu.Item>
            <Button inverted icon="arrow circle up" onClick={(e) => go_dashboard(e)} aria-label="Scroll to dashboard" />
          </Menu.Item>}
        />
        <Menu.Menu position='right'>
          {props.searchable &&
            <Menu.Item>
              <Input icon='search' iconPosition='left' placeholder='Search...' onChange={props.onSearch} />
            </Menu.Item>
          }
          <Menu.Item>
            <DatePicker onDate={props.onDate} name="report_date_string" value={props.report_date_string} label="Report date" />
          </Menu.Item>
          <Menu.Item>
            {(props.user !== null) ? <Logout email={props.email} user={props.user} set_user={props.set_user} /> : <Login set_user={props.set_user} />}
          </Menu.Item>
        </Menu.Menu>
      </Container>
    </Menu>
  )
}
