import React, { Component } from 'react';
import { Button, Container, Form, Header, Icon, Image, Input, Label, Menu, Modal, Popup } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import { ReportTitleContainer } from './ReportTitle.js'

class Login extends Component {
  constructor(props) {
    super(props);
    this.state = { username: '', password: '' }
  }
  handleChange = (e, { name, value }) => this.setState({ [name]: value })
  handleSubmit = () => {
    const { username, password } = this.state;
    this.props.login(username, password);
  }
  render() {
    return (
      <Modal trigger={<Button>Login</Button>} size='small'>
        <Header content='Login' />
        <Modal.Content>
          <Form onSubmit={this.handleSubmit}>
            <Form.Input label='Username' name='username' onChange={this.handleChange} />
            <Form.Input type='password' label='Password' name='password' onChange={this.handleChange} />
            <Form.Button>Submit</Form.Button>
          </Form>
        </Modal.Content>
      </Modal>
    )
  }
}

function Logout(props) {
  return (
    <Button onClick={props.logout}>Logout {props.user}</Button>
  )
}

function NewMeasurementsLabel(props) {
  if (props.nr_new_measurements === 0) { return null }
  const plural_s = props.nr_new_measurements > 1 ? 's' : '';
  return (
    <Popup trigger={
      <Label as='a' circular color='blue' onClick={props.onClick} onKeyPress={props.onClick}>
        {props.nr_new_measurements}
      </Label>}
      content={`Click to retrieve ${props.nr_new_measurements} new measurement${plural_s}`}
    />
  )
}

function Menubar(props) {
  const today = new Date();
  const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
  return (
    <Menu fixed='top' inverted>
      <Container fluid>
        <Menu.Item header>
          {props.report === null ?
            <Image size='mini' src='/favicon.ico' />
            :
            <Button icon compact color='black' onClick={props.go_home}>
              <Icon name='home' size='big' />
            </Button>
          }
        </Menu.Item>
        <Menu.Item>
          {props.report === null ?
            <font size="+3">Quality-time</font>
            :
            <ReportTitleContainer report={props.report} reload={props.reload} user={props.user} />
          }
          <NewMeasurementsLabel onClick={props.reload} nr_new_measurements={props.nr_new_measurements} />
        </Menu.Item>
        <Menu.Menu position='right'>
          <Menu.Item>
            <Input icon='search' iconPosition='left' placeholder='Search...' onChange={props.onSearch} />
          </Menu.Item>
          <Menu.Item>
            <DateInput name="report_date_string" value={props.report_date_string}
              placeholder={today_string} closable={true} initialDate={today}
              maxDate={today} iconPosition="left" onChange={props.onDate} />
          </Menu.Item>
          <Menu.Item>
            {(props.user !== null) ? <Logout user={props.user} logout={props.logout} /> : <Login login={props.login} />}
          </Menu.Item>
        </Menu.Menu>
      </Container>
    </Menu>
  )
}

export { Menubar };
