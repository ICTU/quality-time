import React from 'react';
import PropTypes from 'prop-types';
import { datePropType, optionalDatePropType } from '../sharedPropTypes';
import { Message } from 'semantic-ui-react';

function ErrorMessage({ children }) {
    return (
        <Message warning size='huge'>
            <Message.Header>
                {children}
            </Message.Header>
        </Message>
    )
}
ErrorMessage.propTypes = {
    children: PropTypes.string
}

export function ReportErrorMessage({ reportDate }) {
    return (
        <ErrorMessage>
            {reportDate ? `Sorry, this report didn't exist at ${reportDate}` : "Sorry, this report doesn't exist"}
        </ErrorMessage>
    )
}
ReportErrorMessage.propTypes = {
    reportDate: optionalDatePropType
}

export function ReportsOverviewErrorMessage({ reportDate }) {
    return (
        <ErrorMessage>
            {`Sorry, no reports existed at ${reportDate}`}
        </ErrorMessage>
    )
}
ReportsOverviewErrorMessage.propTypes = {
    reportDate: datePropType
}