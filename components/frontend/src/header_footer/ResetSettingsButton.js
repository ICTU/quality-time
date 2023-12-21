import React from 'react';
import PropTypes from 'prop-types';
import { Button, Icon } from 'semantic-ui-react';
import { Popup } from '../semantic_ui_react_wrappers';
import { optionalDatePropType, settingsPropType } from '../sharedPropTypes';

export function ResetSettingsButton({ atReportsOverview, handleDateChange, reportDate, settings }) {
    const label = `Reset ${atReportsOverview ? "reports overview" : "this report's"} settings`
    return (
        <Popup
            on={["hover", "focus"]}
            trigger={
                <span  // We need a span here to prevent the popup from becoming disabled whenever the button is disabled
                >
                    <Button
                        aria-label={label}
                        basic
                        disabled={settings.allDefault() && reportDate === null}
                        icon
                        onClick={() => {
                            handleDateChange(null);
                            settings.reset()
                        }}
                        inverted
                    >
                        <Icon.Group>
                            <Icon name="undo alternate" />
                            <Icon name="setting" size="tiny" />
                        </Icon.Group>
                    </Button>
                </span>
            }
            content={label}
        />
    )
}
ResetSettingsButton.propTypes = {
    atReportsOverview: PropTypes.bool,
    handleDateChange: PropTypes.func,
    reportDate: optionalDatePropType,
    settings: settingsPropType,
}
