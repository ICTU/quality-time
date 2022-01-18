import React, { useState } from 'react';
import { Header, Icon, Segment } from 'semantic-ui-react';
import './HeaderWithDetails.css';

export function HeaderWithDetails(props) {
    const [show_details, setShowDetails] = useState(false);
    return (
        <Segment basic aria-expanded={show_details} className={props.className} style={{ backgroundColor: "white", paddingLeft: "0px", paddingRight: "0px" }}>
            <Header
                as={props.level}
                onClick={() => setShowDetails(!show_details)}
                onKeyPress={() => setShowDetails(!show_details)}
                style={props.style}
                tabIndex="0"
            >
                <Icon className="Caret" title="expand" name={show_details ? "caret down" : "caret right"} size='large' />
                <Header.Content>
                    {props.header}
                    <Header.Subheader>{props.subheader}</Header.Subheader>
                </Header.Content>
            </Header>
            {show_details && <Segment>{props.children}</Segment>}
        </Segment>
    )
}
