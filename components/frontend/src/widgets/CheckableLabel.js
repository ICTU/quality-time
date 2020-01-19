import React from 'react';
import { Checkbox } from 'semantic-ui-react';

export function CheckableLabel(props) {
    return (
        <label>
            {props.label}
            <Checkbox className="field" label={props.checkbox_label} onClick={props.onClick} slider style={{ paddingLeft: "1cm" }} tabIndex="0" />
        </label>);
}