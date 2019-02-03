import React from 'react';
import { Container, Image, Input, Label, Menu, Popup } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import { ReportTitleContainer } from './ReportTitle.js'


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
      <Container>
        <Menu.Item header>
          <Image size='mini' src='/favicon.ico' style={{ marginRight: '1.5em' }} />
          <ReportTitleContainer report_date={props.report_date} />
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
        </Menu.Menu>
      </Container>
    </Menu>
  )
}

export { Menubar };
