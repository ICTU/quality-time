import React from 'react';
import SemanticDatepicker from 'react-semantic-ui-datepickers';
import 'react-semantic-ui-datepickers/dist/react-semantic-ui-datepickers.css';

export function DatePicker(props) {
    return (
        <SemanticDatepicker
            filterDate={(date) => {return (date.getTime() < (new Date()).getTime())}}
            inverted
            onChange={props.onDate}
            value={props.value}
        />
    )
}
