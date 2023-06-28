import { Icon } from '../semantic_ui_react_wrappers';
import { HyperLink } from './HyperLink';

export function LabelWithHyperLink({labelId, label, url }){
    return (
        <label id={labelId}>
            {label}{" "}
            <HyperLink url={url}>
                <Icon name="help circle" link tabIndex="0" />
            </HyperLink>
        </label>
    )
}
