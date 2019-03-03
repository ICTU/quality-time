import React from 'react';
import { Button, Container, Icon, Image, Input, Label, Menu, Popup } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import { ReportTitleContainer } from './ReportTitle.js'

function Login(props) {
  return (
    <Button onClick={props.login}>Login</Button>
  )
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
            {(props.user !== null) ? <Logout user={props.user} logout={props.logout} /> : <Login login={props.login}/>}
          </Menu.Item>
        </Menu.Menu>
      </Container>
    </Menu>
  )
}

export { Menubar };
