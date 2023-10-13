import React from 'react';
import PropTypes from 'prop-types';
import { Dropdown, Icon } from 'semantic-ui-react';
import { uiModePropType } from '../sharedPropTypes';

export function UIModeMenu({ setUIMode, uiMode }) {
    const style = { textShadow: "0px 0px" }
    return (
        <Dropdown
            icon={
                <Icon.Group aria-label="Dark/light mode" size="big">
                    <Icon corner="top left" name="sun" style={style} />
                    <Icon corner="bottom right" name="moon" style={style} />
                </Icon.Group>
            }
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
