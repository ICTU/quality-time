import TimeAgo from 'react-timeago'
import { LabelWithHelp } from './LabelWithHelp';

export function LabelWithDate({date, labelId, label, help}){
    return (
        <LabelWithHelp
            id={labelId}
            label={<>{label}<LabelDate date={date}/></>}
            help={help}
        />
    )
}

export function LabelDate({date}){
    return date ? <span> (<TimeAgo date={date} />)</span> : null
}
