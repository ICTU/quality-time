import React, { useState } from 'react';
import { Button, Dropdown, Icon, Popup } from 'semantic-ui-react';
import { get_report_pdf } from '../api/report';
import { show_message } from '../utils'
import { ItemBreadcrumb } from './ItemBreadcrumb';

function ActionButton(props) {
  const { action, icon, item_type, popup, position, ...other } = props;
  const button = <Button basic icon primary {...other} ><Icon name={icon} /> {action} {item_type}</Button>;
  return (
    popup ?
      <Popup
        content={popup}
        position={position || 'top left'}
        trigger={button}
      /> :
      button
  )
}

export function AddButton(props) {
  return <ActionButton icon='plus' action='Add' popup={`Add a new ${props.item_type} here`} {...props} />
}

export function DeleteButton(props) {
  return (
    <ActionButton
      action='Delete'
      floated='right'
      icon='trash'
      negative
      popup={`Delete this ${props.item_type}. Careful, this can only be undone by a system administrator!`}
      position='top right'
      {...props}
    />
  )
}

function download_pdf(report_uuid, query_string, callback) {
  get_report_pdf(report_uuid, query_string)
    .then(response => {
      if (response.ok === false) {
        show_message("error", "PDF rendering failed", "HTTP code " + response.status + ": " + response.statusText)
      } else {
        let url = window.URL.createObjectURL(response);
        let a = document.createElement('a');
        a.href = url;
        let now = new Date();
        a.download = `Quality-time-report-${report_uuid}-${now.toISOString()}.pdf`;
        a.click();
      }
    }).finally(() => callback());
}

export function DownloadAsPDFButton(props) {
  const [loading, setLoading] = useState(false);
  const { report_uuid, query_string, ...otherProps } = props;
  return (
    <ActionButton
      action='Download'
      icon="file pdf"
      item_type='report as pdf'
      loading={loading}
      onClick={() => {
        if (!loading) {
          setLoading(true);
          download_pdf(report_uuid, query_string, () => { setLoading(false) })
        }
      }}
      {...otherProps}
    />
  )
}

function ReorderButton(props) {
  const label = `Move ${props.moveable} to the ${props.direction} ${props.slot || 'position'}`;
  const icon = { "first": "double up", "last": "double down", "previous": "up", "next": "down" }[props.direction];
  const disabled = (props.first && (props.direction === "first" || props.direction === "previous")) ||
    (props.last && (props.direction === "last" || props.direction === "next"));
  return (
    <Popup content={label} trigger={
      <Button
        aria-label={label}
        basic
        disabled={disabled}
        icon={`angle ${icon}`}
        onClick={() => props.onClick(props.direction)}
        primary
      />}
    />
  )
}

export function ReorderButtonGroup(props) {
  return (
    <Button.Group style={{ marginTop: "0px" }}>
      <ReorderButton {...props} direction="first" />
      <ReorderButton {...props} direction="previous" />
      <ReorderButton {...props} direction="next" />
      <ReorderButton {...props} direction="last" />
    </Button.Group>
  )
}

function ActionAndItemPickerButton(props) {
  const [options_loaded, setOptionsLoaded] = useState(false);
  const [options, setOptions] = useState([]);

  var { action, item_type, onChange, get_options, icon } = props;
  var breadcrumb_props = { report: "report" };
  if (item_type !== 'report') {
    breadcrumb_props.subject = 'subject';
    if (item_type !== 'subject') {
      breadcrumb_props.metric = 'metric';
      if (item_type !== 'metric') {
        breadcrumb_props.source = 'source';
      }
    }
  }
  return (
    <Popup
      content={`${action} an existing ${item_type} here`}
      trigger={
        <Dropdown
          basic
          className='button icon primary'
          floating
          header={<Dropdown.Header><ItemBreadcrumb size='tiny' {...breadcrumb_props} /></Dropdown.Header>}
          options={options}
          onChange={(event, { value }) => onChange(value)}
          onOpen={() => { if (!options_loaded) { setOptions(get_options()); setOptionsLoaded(true); } }}
          scrolling
          selectOnBlur={false}
          selectOnNavigation={false}
          trigger={<><Icon name={icon} /> {`${action} ${item_type} `}</>}
        />}
    />
  )
}

export function CopyButton(props) {
  return (
    <ActionAndItemPickerButton {...props} action="Copy" icon="copy" />
  )
}

export function MoveButton(props) {
  return (
    <ActionAndItemPickerButton {...props} action="Move" icon="shuffle" />
  )
}
