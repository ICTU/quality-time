import TimeAgo from 'react-timeago';
import { oneOfType, string } from 'prop-types';
import { LabelWithHelp } from './LabelWithHelp';
import { datePropType, labelPropType, popupContentPropType } from '../sharedPropTypes';

export function LabelWithDate({date, labelId, label, help}){
    return (
        <LabelWithHelp
            id={labelId}
            label={<>{label}<LabelDate date={date}/></>}
            help={help}
        />
    )
}
LabelWithDate.propTypes = {
    date: oneOfType([datePropType, string]),
    labelId: string,
    label: labelPropType,
    help: popupContentPropType,
}

export function LabelDate({date}){
    return date ? <span> (<TimeAgo date={date} />)</span> : null
}
LabelDate.propTypes = {
    date: oneOfType([datePropType, string]),
}
