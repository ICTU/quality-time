import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Header, Icon, Segment } from '../semantic_ui_react_wrappers';
import { childrenPropType } from '../sharedPropTypes';
import './HeaderWithDetails.css';

export function HeaderWithDetails({ children, className, header, level, style, subheader }) {
    const [showDetails, setShowDetails] = useState(false);
    const segmentStyle = { paddingLeft: "0px", paddingRight: "0px" }
    return (
        <Segment basic aria-expanded={showDetails} className={className} style={segmentStyle}>
            <Header
                as={level}
                onClick={() => setShowDetails(!showDetails)}
                onKeyPress={(event) => { event.preventDefault(); setShowDetails(!showDetails) }}
                style={style}
                tabIndex="0"
            >
                <Icon className="Caret" title="expand" name={showDetails ? "caret down" : "caret right"} size='large' />
                <Header.Content>
                    {header}
                    <Header.Subheader>{subheader}</Header.Subheader>
                </Header.Content>
            </Header>
            {showDetails && <Segment>{children}</Segment>}
        </Segment>
    )
}
HeaderWithDetails.propTypes = {
    children: childrenPropType,
    className: PropTypes.string,
    header: PropTypes.node,
    level: PropTypes.string,
    style: PropTypes.object,
    subheader: PropTypes.element,
}