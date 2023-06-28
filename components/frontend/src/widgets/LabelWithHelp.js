import { Icon, Popup } from '../semantic_ui_react_wrappers';

export function LabelWithHelp({labelId, label, help, hoverable}){
    return (
        <label id={labelId}>
            {label}{" "}
            <Popup
                hoverable={hoverable}
                on={["hover", "focus"]}
                content={help}
                trigger={<Icon data-testid="help-icon" tabIndex="0" name="help circle" />}
            />
        </label>
    )
}
