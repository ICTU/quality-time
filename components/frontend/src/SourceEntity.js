import React, { Component } from 'react';
import { Table } from 'semantic-ui-react';
import { TableRowWithDetails } from './TableRowWithDetails';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';

export class SourceEntity extends Component {
  render() {
    let props = this.props;
    const ignored_entity = ["wont_fix", "fixed", "false_positive"].indexOf(props.status) > -1;
    if (props.hide_ignored_entities && ignored_entity) {
      return null;
    }
    ;
    const style = ignored_entity ? { textDecoration: "line-through" } : {};
    var positive, negative, warning, active;
    props.entity_attributes.forEach((entity_attribute) => {
      let cell_contents = props.entity[entity_attribute.key];
      if (entity_attribute.color && entity_attribute.color[cell_contents]) {
        positive = (entity_attribute.color[cell_contents] === "positive");
        negative = (entity_attribute.color[cell_contents] === "negative");
        warning = (entity_attribute.color[cell_contents] === "warning");
        active = (entity_attribute.color[cell_contents] === "active");
        return;
      }
    });
    const details = <SourceEntityDetails name={props.entity_name} status={props.status} rationale={props.rationale} readOnly={props.readOnly} set_entity_attribute={props.set_entity_attribute} source_uuid={props.source_uuid} entity={props.entity} />;
    return (<TableRowWithDetails key={props.entity.key} style={style} details={details} active={active} positive={positive} negative={negative} warning={warning}>
      {props.entity_attributes.map((entity_attribute, col_index) => <Table.Cell key={col_index}>
        <SourceEntityAttribute entity={props.entity} entity_attribute={entity_attribute} />
      </Table.Cell>)}
    </TableRowWithDetails>);
  }
}
