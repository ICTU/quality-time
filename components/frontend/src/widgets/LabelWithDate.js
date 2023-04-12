import { Icon, Popup } from '../semantic_ui_react_wrappers';
import TimeAgo from 'react-timeago'

export function LabelWithDate({currentValueDate, labelId, help, labelText }){
    return (
        <label id={labelId}>
            {labelText}
            <LabelDate date={currentValueDate} />{" "}
            <Popup
                on={["hover", "focus"]}
                content={help}
                trigger={<Icon tabIndex="0" name="help circle" />}
            />
        </label>
    )
}
export function LabelDate({date}){
    return date ? <span> (<TimeAgo date={date} />)</span> : null
}