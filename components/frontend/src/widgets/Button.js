import React from 'react';
import { Button, Dropdown, Icon, Popup } from 'semantic-ui-react';

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

export function DownloadAsPDFButton(props) {
  return <ActionButton icon="file pdf" action='Download' item_type='report as pdf' {...props} />
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
  var { marginTop, ...otherProps } = props;
  return (
    <Button.Group style={{ marginTop: marginTop || "0px" }}>
      <ReorderButton {...otherProps} direction="first" />
      <ReorderButton {...otherProps} direction="previous" />
      <ReorderButton {...otherProps} direction="next" />
      <ReorderButton {...otherProps} direction="last" />
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
        text={`Move ${item_type} to`}
        selectOnBlur={false}
        selectOnNavigation={false}
        {...otherProps} />
    </Button>
  )
}

export function ItemActionButtons(props) {
  return (
    <>
      <CopyButton item_type={props.item_type} onClick={props.onCopy} />
      <MoveButton item_type={props.item_type} onClick={props.onMove} options={props.options} />
      <ReorderButtonGroup first={props.first_item} last={props.last_item} moveable={props.item_type} onClick={props.onReorder} slot={props.slot || "position"} />
      <DeleteButton item_type={props.item_type} onClick={props.onDelete} />
    </>
  )
}