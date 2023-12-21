import React from 'react';
import PropTypes from 'prop-types';
import { Dropdown } from 'semantic-ui-react';
import { uiModePropType } from '../sharedPropTypes';
import { IconCombi } from '../widgets/IconCombi'

export function UIModeMenu({ setUIMode, uiMode }) {
    return (
        <Dropdown
            icon={<IconCombi iconBottomRight="moon" iconTopLeft="sun" label="Dark/light mode" />}
        >
            <Dropdown.Menu>
                <Dropdown.Header>Dark/light mode</Dropdown.Header>
                <Dropdown.Item active={uiMode === "follow_os"} onClick={() => setUIMode("follow_os")}>
                    Follow OS setting
                </Dropdown.Item>
                <Dropdown.Item active={uiMode === "dark"} onClick={() => setUIMode("dark")}>
                    Dark mode
                </Dropdown.Item>
                <Dropdown.Item active={uiMode === "light"} onClick={() => setUIMode("light")}>
                    Light mode
                </Dropdown.Item>
            </Dropdown.Menu>
        </Dropdown>
    )
}
UIModeMenu.propTypes = {
    setUIMode: PropTypes.func,
    uiMode: uiModePropType
}
