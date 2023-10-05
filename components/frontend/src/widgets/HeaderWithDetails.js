import React, { useState } from 'react';
import { Header, Icon, Segment } from '../semantic_ui_react_wrappers';
import './HeaderWithDetails.css';

export function HeaderWithDetails({ children, className, header, level, style, subheader }) {
    const [show_details, setShowDetails] = useState(false);
    const segmentStyle = { paddingLeft: "0px", paddingRight: "0px" }
    return (
        <Segment basic aria-expanded={show_details} className={className} style={segmentStyle}>
            <Header
                as={level}
                onClick={() => setShowDetails(!show_details)}
                onKeyPress={(event) => { event.preventDefault(); setShowDetails(!show_details) }}
                style={style}
                tabIndex="0"
            >
                <Icon className="Caret" title="expand" name={show_details ? "caret down" : "caret right"} size='large' />
                <Header.Content>
                    {header}
                    <Header.Subheader>{subheader}</Header.Subheader>
                </Header.Content>
            </Header>
            {show_details && <Segment>{children}</Segment>}
        </Segment>
    )
}
