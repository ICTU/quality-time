import React from 'react';
import { Checkbox } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

export function CheckableLabel(props) {
    const checkable_label = props.checkable ?
        (<label>
            {props.label}
            <Checkbox className="field" label={props.checkbox_label} onClick={props.onClick} slider style={{ paddingLeft: "1cm" }} tabIndex="0" />
        </label>) : props.label;
    return <ReadOnlyOrEditable readOnlyComponent={props.label} editableComponent={checkable_label}/>;
}