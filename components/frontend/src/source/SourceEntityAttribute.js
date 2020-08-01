import React from 'react';
import TimeAgo from 'react-timeago';
import { StatusIcon } from '../metric/StatusIcon';

function DateAndTimeAgo(date_string, include_time) {
  const date = new Date(date_string);
  const locale_string = include_time ? date.toLocaleString() : date.toLocaleDateString();
  return <>{locale_string} <font color="grey">(<TimeAgo date={date_string} />)</font></>;
}

export function SourceEntityAttribute(props) {
  let cell_contents = props.entity[props.entity_attribute.key] || "";
  cell_contents = cell_contents && props.entity_attribute.type === "datetime" ? DateAndTimeAgo(cell_contents, true) : cell_contents;
  cell_contents = cell_contents && props.entity_attribute.type === "date" ? DateAndTimeAgo(cell_contents, false) : cell_contents;
  cell_contents = cell_contents && props.entity_attribute.type === "status" ? <StatusIcon status={cell_contents} /> : cell_contents;
  cell_contents = props.entity[props.entity_attribute.url] ? <a href={props.entity[props.entity_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.entity_attribute.pre ? <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{cell_contents}</pre> : cell_contents;
  return (cell_contents);
}
