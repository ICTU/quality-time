import React, { useState } from 'react';
import { Button, Dropdown, Icon, Popup } from 'semantic-ui-react';
import { get_report_pdf } from '../api/report';
import { show_message } from '../utils'
import { ItemBreadcrumb } from './ItemBreadcrumb';

function ActionButton(props) {
  const { action, icon, item_type, ...other } = props;
  return (
    <Button
      basic
      icon
      primary
      {...other}
    >
      <Icon name={icon} /> {action} {item_type}
    </Button>
  )
}

export function AddButton(props) {
  return <ActionButton icon='plus' action='Add' {...props} />
}

export function CopyButton(props) {
  return <ActionButton icon='copy' action='Copy' {...props} />
}

export function DeleteButton(props) {
  return <ActionButton icon='trash' action='Delete' negative floated='right' {...props} />
}

function download_pdf(report_uuid, callback) {
  get_report_pdf(report_uuid)
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
  const { report_uuid, ...otherProps } = props;
  return (
      <ActionButton
          action='Download'
          icon="file pdf"
          item_type='report as pdf'
          loading={loading}
          onClick={() => {
              if (!loading) {
                  setLoading(true);
                  download_pdf(report_uuid, () => { setLoading(false) })
              }
          }}
          {...otherProps}
      />
  )
}

function ReorderButton(props) {
  const label = `Move ${props.moveable} to the ${props.direction} ${props.slot}`;
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

export function MoveButton(props) {
  var { item_type, onClick, ...otherProps } = props;
  return (
    <Button basic icon primary>
      <Icon name="shuffle" />&nbsp;
      <Dropdown
        basic
        onChange={(event, { value }) => onClick(value)}
        scrolling
        selectOnBlur={false}
        selectOnNavigation={false}
        text={`Move ${item_type} to`}
        {...otherProps} />
    </Button>
  )
}

export function AddOrCopyButton(props) {
  var { item_type, onChange, onClick, options } = props;
  var breadcrumb_props = {report: "copy existing report"};
  if (item_type === 'subject') {
    breadcrumb_props.subject = 'subject';
  }
  return (
    <Button.Group basic icon primary>
      <Dropdown
        basic
        className='button icon'
        disabled={options.length === 0}
        floating
        header={<Dropdown.Header><ItemBreadcrumb size='tiny' {...breadcrumb_props}/></Dropdown.Header>}
        options={options}
        onChange={(event, { value }) => onChange(value)}
        scrolling
        selectOnBlur={false}
        selectOnNavigation={false}
        trigger={<React.Fragment/>}
      />
      <AddButton onClick={onClick} item_type={item_type} />
    </Button.Group>
  )
}

export function ItemActionButtons(props) {
  return (
    <>
      <CopyButton item_type={props.item_type} onClick={props.onCopy} />
      <MoveButton item_type={props.item_type} onClick={props.onMove} options={props.options} header={props.reorder_header} />
      <ReorderButtonGroup first={props.first_item} last={props.last_item} moveable={props.item_type} onClick={props.onReorder} slot={props.slot || "position"} />
      <DeleteButton item_type={props.item_type} onClick={props.onDelete} />
    </>
  )
}