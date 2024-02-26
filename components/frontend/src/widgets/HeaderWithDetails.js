import { node, object, string } from 'prop-types';
import { Header, Icon, Segment } from '../semantic_ui_react_wrappers';
import { childrenPropType, settingsPropType } from '../sharedPropTypes';
import './HeaderWithDetails.css';

export function HeaderWithDetails({ children, className, header, item_uuid, level, style, settings, subheader }) {
    const showDetails = settings.expandedItems.includes(item_uuid)
    const segmentStyle = { paddingLeft: "0px", paddingRight: "0px" }
    return (
        <Segment basic aria-expanded={showDetails} className={className} style={segmentStyle}>
            <Header
                as={level}
                onClick={() => settings.expandedItems.toggle(item_uuid)}
                onKeyPress={(event) => { event.preventDefault(); settings.expandedItems.toggle(item_uuid) }}
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
    className: string,
    header: node,
    item_uuid: string,
    level: string,
    settings: settingsPropType,
    style: object,
    subheader: string,
}
