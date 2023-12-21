import React from 'react';
import { Button, Icon } from 'semantic-ui-react';
import { Popup } from '../semantic_ui_react_wrappers';
import { stringsURLSearchQueryPropType } from '../sharedPropTypes';

export function CollapseButton({ expandedItems }) {
    const label = "Collapse all headers and metrics"
    return (
        <Popup
            on={["hover", "focus"]}
            trigger={
                <span  // We need a span here to prevent the popup from becoming disabled whenever the button is disabled
                >
                    <Button
                        aria-label={label}
                        basic
                        disabled={expandedItems.equals([])}
                        icon
                        onClick={() => expandedItems.reset()}
                        inverted
                    >
                        <Icon name="angle double up" />
                    </Button>
                </span>
            }
            content={label}
        />
    )
}
CollapseButton.propTypes = {
    expandedItems: stringsURLSearchQueryPropType
}
