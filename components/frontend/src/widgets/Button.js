import React from 'react';
import { Button, Icon, Popup } from 'semantic-ui-react';

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

function MoveButton(props) {
    const label = `Move ${props.moveable} to the ${props.direction} ${props.slot}`;
    const icon = {"first": "double up", "last": "double down", "previous": "up", "next": "down"}[props.direction];
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

  export function MoveButtonGroup(props) {
    var { marginTop, ...otherProps } = props;
    return (
      <Button.Group style={{ marginTop: marginTop || "0px" }}>
        <MoveButton {...otherProps} direction="first" />
        <MoveButton {...otherProps} direction="previous" />
        <MoveButton {...otherProps} direction="next" />
        <MoveButton {...otherProps} direction="last" />
      </Button.Group>
    )
  }