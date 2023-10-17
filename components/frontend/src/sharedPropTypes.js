import PropTypes from 'prop-types';

export const datePropType = PropTypes.instanceOf(Date)

export const datesPropType = PropTypes.arrayOf(datePropType)

export const issueSettingsPropType = PropTypes.shape({
    showIssueCreationDate: PropTypes.bool,
    showIssueDueDate: PropTypes.bool,
    showIssueRelease: PropTypes.bool,
    showIssueSprint: PropTypes.bool,
    showIssueSummary: PropTypes.bool,
    showIssueUpdateDate: PropTypes.bool
})

export const metricsToHidePropType = PropTypes.oneOf(["none", "all", "no_action_needed"])

export const reportPropType = PropTypes.shape({
    issue_tracker: PropTypes.object,
})

export const reportsPropType = PropTypes.arrayOf(reportPropType)

export const sortDirectionPropType = PropTypes.oneOf(["ascending", "descending"])

export const stringsPropType = PropTypes.arrayOf(PropTypes.string)

export const uiModePropType = PropTypes.oneOf(["dark", "light", "follow_os"])
