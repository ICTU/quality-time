import React from 'react';
import { Dropdown } from 'semantic-ui-react';

export function LabelWithDropdown(props) {
    const { label, ...otherProps } = props;
    return (
        <label>
            {label}
            <span style={{ paddingLeft: "6mm", color: props.color || "black" }}>
                {props.prefix}&nbsp;<Dropdown inline tabIndex="0" {...otherProps} />
            </span>
        </label>
    );
}