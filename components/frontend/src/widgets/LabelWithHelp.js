import { Icon, Popup } from '../semantic_ui_react_wrappers';

export function LabelWithHelp({labelId, labelFor, label, help, hoverable}){
    return (
        <label id={labelId} htmlFor={labelFor}>
            {label}{" "}
            <Popup
                hoverable={hoverable}
                on={["hover", "focus"]}
                content={help}
                trigger={<Icon data-testid="help-icon" tabIndex="0" name="help circle" />}
                wide
            />
        </label>
    )
}
