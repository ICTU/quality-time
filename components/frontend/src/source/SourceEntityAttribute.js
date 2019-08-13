import React from 'react';

export function SourceEntityAttribute(props) {
  let cell_contents = props.entity[props.entity_attribute.key];
  cell_contents = cell_contents && props.entity_attribute.type === "datetime" ? new Date(cell_contents).toLocaleString() : cell_contents;
  cell_contents = cell_contents && props.entity_attribute.type === "date" ? new Date(cell_contents).toLocaleDateString() : cell_contents;
  cell_contents = props.entity[props.entity_attribute.url] ? <a href={props.entity[props.entity_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.entity_attribute.pre ? <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{cell_contents}</pre> : cell_contents;
  return (cell_contents);
}
