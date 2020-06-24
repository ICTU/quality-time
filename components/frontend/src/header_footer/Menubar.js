import React, { useState } from 'react';
import { Button, Container, Form, Header, Icon, Image, Input, Menu, Message, Modal, Dropdown, Popup } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import { Avatar } from '../widgets/Avatar';
import './Menubar.css';

function Login(props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  return (
    <Modal trigger={<Button secondary><Icon name='user' />Login</Button>} size='tiny'>
      <Header content='Login' />
      <Modal.Content>
        <Form error={props.error} warning={!props.error} onSubmit={() => props.login(username, password)}>
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
      options={[{ key: "logout", text: "Logout", icon: "log out", onClick: props.logout }]}
    />
  )
}

export function Menubar(props) {
  const today = new Date();
  const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
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
            <Button inverted icon="arrow circle up" onClick={(e) => props.go_dashboard(e)} />
          </Menu.Item>}
        />
        <Menu.Menu position='right'>
          {props.searchable &&
            <Menu.Item>
              <Input icon='search' iconPosition='left' placeholder='Search...' onChange={props.onSearch} />
            </Menu.Item>
          }
          <Menu.Item>
            <DateInput
              animation="none"  // Work-around for https://github.com/arfedulov/semantic-ui-calendar-react/issues/152
              clearable
              closable
              iconPosition="left"
              initialDate={today}
              maxDate={today}
              name="report_date_string"
              onChange={props.onDate}
              placeholder={today_string}
              value={props.report_date_string}
              aria-label="Report date"
            />
          </Menu.Item>
          <Menu.Item>
            {(props.user !== null) ? <Logout email={props.email} user={props.user} logout={props.logout} /> : <Login login={props.login} error={props.login_error} />}
          </Menu.Item>
        </Menu.Menu>
      </Container>
    </Menu>
  )
}
