import PropTypes from 'prop-types';

export const issueSettingsPropType = PropTypes.shape({
    showIssueCreationDate: PropTypes.bool,
    showIssueDueDate: PropTypes.bool,
    showIssueRelease: PropTypes.bool,
    showIssueSprint: PropTypes.bool,
    showIssueSummary: PropTypes.bool,
    showIssueUpdateDate: PropTypes.bool
})

export const sortDirectionPropType = PropTypes.oneOf(["ascending", "descending"])

export const datePropType = PropTypes.instanceOf(Date)

export const datesPropType = PropTypes.arrayOf(datePropType)

export const uiModePropType = PropTypes.oneOf(["dark", "light", "follow_os"])
