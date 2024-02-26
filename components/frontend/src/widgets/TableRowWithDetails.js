import { Icon, Table } from '../semantic_ui_react_wrappers';
import { bool, func, object } from 'prop-types';
import { childrenPropType } from '../sharedPropTypes';

export function TableRowWithDetails(props) {
    const { children, details, expanded, onExpand, style, ...otherProps } = props;
    return (
        <>
            <Table.Row {...otherProps}>
                <Table.Cell
                    aria-label="Expand/collapse"
                    collapsing
                    onClick={() => onExpand(!expanded)}
                    onKeyPress={(event) => { event.preventDefault(); onExpand(!expanded) }}
                    tabIndex="0"
                    textAlign="center"
                    style={style}
                    role="button"
                >
                    <Icon size='large' name={expanded ? "caret down" : "caret right"} />
                </Table.Cell>
                {children}
            </Table.Row>
            {expanded &&
                <Table.Row>
                    <Table.Cell colSpan="99">
                        {details}
                    </Table.Cell>
                </Table.Row>}
        </>
    );
}
TableRowWithDetails.propTypes = {
    children: childrenPropType,
    details: childrenPropType,
    expanded: bool,
    onExpand: func,
    style: object,
}
