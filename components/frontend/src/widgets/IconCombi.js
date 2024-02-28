import PropTypes from 'prop-types';
import { Icon } from 'semantic-ui-react';

export function IconCombi({ iconBottomRight, iconTopLeft, label }) {
    const style = { textShadow: "0px 0px" }
    return (
        <Icon.Group aria-label={label} size="big">
            <Icon corner="top left" name={iconTopLeft} style={style} />
            <Icon corner="bottom right" name={iconBottomRight} style={style} />
        </Icon.Group>
    )
}
IconCombi.propTypes = {
    iconBottomRight: PropTypes.string,
    iconTopLeft: PropTypes.string,
    label: PropTypes.string,
}
