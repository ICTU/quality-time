import React, { useState } from 'react';
import { Button, Container, Form, Header, Icon, Image, Input, Menu, Message, Modal, Dropdown } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import md5 from 'md5';
import './Menubar.css';

function Login(props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  return (
    <Modal trigger={<Button secondary><Icon name='user' />Login</Button>} size='tiny'>
      <Header content='Login' />
      <Modal.Content>
        <Form error={props.error} warning={!props.error} onSubmit={() => props.login(username, password)}>
          <Form.Input autoFocus label='Username' name='username' onChange={(event, { name, value }) => setUsername(value)} />
          <Form.Input type='password' label='Password' name='password' onChange={(event, { name, value }) => setPassword(value)} />
          <Message error header='Invalid credentials' content='Username and/or password are invalid. Please try again.' />
          <Message warning header='Heads up' content='Changes you make after you log in, such as adding metrics, changing metric targets, and marking issues as false positive, are logged.' />
          <Form.Button>Submit</Form.Button>
        </Form>
      </Modal.Content>
    </Modal>
  )
}

function Logout(props) {
  const trigger = <><Image avatar src={`https://www.gravatar.com/avatar/${md5(props.email || '')}?d=identicon`} /> {props.user}</>
  return (
    <Dropdown
      trigger={trigger}
      options={[{key: "logout", text: "Logout", icon: "log out", onClick: props.logout}]}
    />
  )
}

export function Menubar(props) {
  const today = new Date();
  const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
  return (
    <Menu className="Menubar" fixed='top' inverted>
      <Container fluid>
        <Menu.Item header onClick={() => props.go_home()}>
          <Image size='mini' src='/favicon.ico' />
        </Menu.Item>
        <Menu.Item>
          <font size="+3">Quality-time</font>
        </Menu.Item>
        <Menu.Menu position='right'>
          {props.searchable &&
            <Menu.Item>
              <Input icon='search' iconPosition='left' placeholder='Search...' onChange={props.onSearch} />
            </Menu.Item>
          }
          <Menu.Item>
            <DateInput
              animation="none"  // Work-around for https://github.com/arfedulov/semantic-ui-calendar-react/issues/152
              closable={true}
              iconPosition="left"
              initialDate={today}
              maxDate={today}
              name="report_date_string"
              onChange={props.onDate}
              placeholder={today_string}
              value={props.report_date_string}
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
