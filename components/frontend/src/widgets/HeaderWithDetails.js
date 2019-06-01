import React, { useState } from 'react';
import { Header, Icon } from 'semantic-ui-react';

export function HeaderWithDetails(props) {
    const [show_details, setShowDetails] = useState(false);
    return (
        <>
            <Header
                as={props.level}
                onClick={() => setShowDetails(!show_details)}
                onKeyPress={() => setShowDetails(!show_details)}
                style={props.style}
                tabIndex="0"
            >
                <Icon name={show_details ? "caret down" : "caret right"} size='large' />
                <Header.Content>
                    {props.header}
                    <Header.Subheader>{props.subheader}</Header.Subheader>
                </Header.Content>
            </Header>
            {show_details && props.children}
        </>
    )
}
