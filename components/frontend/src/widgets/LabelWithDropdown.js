import React from 'react';
import { Dropdown } from 'semantic-ui-react';

export function LabelWithDropdown({ color, direction, label, onChange, options, value}) {
    return (
        <label>
            {label}
            <span style={{ paddingLeft: "6mm", color: color || "black" }}>
                <Dropdown
                    color={color}
                    direction={direction}
                    inline
                    onChange={onChange}
                    options={options}
                    tabIndex="0"
                    value={value}
                />
            </span>
        </label>
    );
}