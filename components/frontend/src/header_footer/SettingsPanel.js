import "./SettingsPanel.css"

import { bool, func, number, string } from "prop-types"
import { Header, Menu, Segment } from "semantic-ui-react"

import { Icon } from "../semantic_ui_react_wrappers"
import {
    boolURLSearchQueryPropType,
    hiddenCardsPropType,
    integerURLSearchQueryPropType,
    metricsToHidePropType,
    metricsToHideURLSearchQueryPropType,
    popupContentPropType,
    settingsPropType,
    sortDirectionPropType,
    sortDirectionURLSearchQueryPropType,
    stringsPropType,
    stringsURLSearchQueryPropType,
    stringURLSearchQueryPropType,
} from "../sharedPropTypes"
import { capitalize, pluralize } from "../utils"
import { SettingsMenuItem } from "./SettingsMenuItem"

export function SettingsPanel({ atReportsOverview, handleSort, settings, tags }) {
    const oneDateColumn = settings.nrDates.equals(1)
    const multipleDateColumns = !oneDateColumn
    const menuProps = { compact: true, vertical: true, inverted: true, secondary: true }
    const dateIntervalMenuItemProps = {
        dateInterval: settings.dateInterval,
        disabled: oneDateColumn,
        help: "The date interval can only be changed when at least two dates are shown",
    }
    const cardsMenuItemProps = { hiddenCards: settings.hiddenCards }
    const metricMenuItemProps = { metricsToHide: settings.metricsToHide }
    const sortColumnMenuItemProps = {
        sortColumn: settings.sortColumn,
        sortDirection: settings.sortDirection,
        handleSort: handleSort,
    }
    const sortOrderMenuItemProps = {
        disabled: oneDateColumn,
        help: "The date order can only be changed when at least two dates are shown",
        sortOrder: settings.dateOrder,
    }
    const visibleColumnMenuItemProps = { hiddenColumns: settings.hiddenColumns }
    return (
        <Segment.Group horizontal className="equal width" style={{ margin: "0px", border: "0px" }}>
            <Segment inverted color="black">
                <Header size="small">Visible cards</Header>
                <Menu {...menuProps}>
                    <VisibleCardsMenuItem cards={atReportsOverview ? "reports" : "subjects"} {...cardsMenuItemProps} />
                    <VisibleCardsMenuItem cards="tags" {...cardsMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Visible metrics</Header>
                <Menu {...menuProps}>
                    <MetricMenuItem hide="none" {...metricMenuItemProps} />
                    <MetricMenuItem hide="no_action_needed" {...metricMenuItemProps} />
                    <MetricMenuItem hide="all" {...metricMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Visible tags</Header>
                <Menu style={{ maxHeight: "450px", overflow: "auto" }} {...menuProps}>
                    {tags.map((tag) => (
                        <VisibleTagMenuItem key={tag} tag={tag} hiddenTags={settings.hiddenTags} />
                    ))}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Visible columns</Header>
                <Menu {...menuProps}>
                    <VisibleColumnMenuItem
                        column="trend"
                        disabled={multipleDateColumns}
                        help="The trend column can only be made visible when one date is shown"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem
                        column="status"
                        disabled={multipleDateColumns}
                        help="The status column can only be made visible when one date is shown"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem
                        column="measurement"
                        disabled={multipleDateColumns}
                        help="The measurement column can only be made visible when one date is shown"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem
                        column="target"
                        disabled={multipleDateColumns}
                        help="The target column can only be made visible when one date is shown"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem column="unit" {...visibleColumnMenuItemProps} />
                    <VisibleColumnMenuItem column="source" {...visibleColumnMenuItemProps} />
                    <VisibleColumnMenuItem column="time_left" {...visibleColumnMenuItemProps} />
                    <VisibleColumnMenuItem
                        column="delta"
                        disabled={oneDateColumn}
                        help="The delta column(s) can only be made visible when at least two dates are shown"
                        itemText="Delta (𝚫)"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem
                        column="overrun"
                        disabled={oneDateColumn}
                        help="The overrun column can only be made visible when at least two dates are shown"
                        {...visibleColumnMenuItemProps}
                    />
                    <VisibleColumnMenuItem column="comment" {...visibleColumnMenuItemProps} />
                    <VisibleColumnMenuItem column="issues" {...visibleColumnMenuItemProps} />
                    <VisibleColumnMenuItem column="tags" {...visibleColumnMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Sort column</Header>
                <Menu {...menuProps}>
                    <SortColumnMenuItem column="name" {...sortColumnMenuItemProps} />
                    <SortColumnMenuItem
                        column="status"
                        disabled={multipleDateColumns || settings.hiddenColumns.includes("status")}
                        help="The status column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="measurement"
                        disabled={multipleDateColumns || settings.hiddenColumns.includes("measurement")}
                        help="The measurement column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="target"
                        disabled={multipleDateColumns || settings.hiddenColumns.includes("target")}
                        help="The target column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="unit"
                        disabled={settings.hiddenColumns.includes("unit")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="source"
                        disabled={settings.hiddenColumns.includes("source")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="time_left"
                        disabled={settings.hiddenColumns.includes("time_left")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="overrun"
                        disabled={settings.nrDates.equals(1) || settings.hiddenColumns.includes("overrun")}
                        help="The overrun column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="comment"
                        disabled={settings.hiddenColumns.includes("comment")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="issues"
                        disabled={settings.hiddenColumns.includes("issues")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="tags"
                        disabled={settings.hiddenColumns.includes("tags")}
                        {...sortColumnMenuItemProps}
                    />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Number of dates</Header>
                <Menu {...menuProps}>
                    {[1, 2, 3, 4, 5, 6, 7].map((nr) => (
                        <NrOfDatesMenuItem key={nr} nr={nr} nrDates={settings.nrDates} />
                    ))}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Time between dates</Header>
                <Menu {...menuProps}>
                    <DateIntervalMenuItem key={1} nr={1} {...dateIntervalMenuItemProps} />
                    {[7, 14, 21, 28].map((nr) => (
                        <DateIntervalMenuItem key={nr} nr={nr} {...dateIntervalMenuItemProps} />
                    ))}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Date order</Header>
                <Menu {...menuProps}>
                    <SortOrderMenuItem order="ascending" {...sortOrderMenuItemProps} />
                    <SortOrderMenuItem order="descending" {...sortOrderMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Visible issue details</Header>
                <Menu {...menuProps}>
                    <IssueAttributeMenuItem
                        issueAttributeName="Summary"
                        issueAttribute={settings.showIssueSummary}
                        help="Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Creation date"
                        issueAttribute={settings.showIssueCreationDate}
                        help="Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Update date"
                        issueAttribute={settings.showIssueUpdateDate}
                        help="Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Due date"
                        issueAttribute={settings.showIssueDueDate}
                        help="Next to the issue status, also show the due date of issues. Note: the popup over the issue always shows the due date, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Release"
                        issueAttribute={settings.showIssueRelease}
                        help="Next to the issue status, also show the release issues are assigned to. Note: the popup over the issue always shows the release, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Sprint"
                        issueAttribute={settings.showIssueSprint}
                        help="Next to the issue status, also show the sprint issues are assigned to. Note: the popup over the issue always shows the sprint, if the issue has one, regardless of this setting."
                    />
                </Menu>
            </Segment>
        </Segment.Group>
    )
}
SettingsPanel.propTypes = {
    handleSort: func,
    tags: stringsPropType.isRequired,
    atReportsOverview: bool,
    settings: settingsPropType,
}

function VisibleCardsMenuItem({ cards, hiddenCards }) {
    return (
        <SettingsMenuItem active={!hiddenCards.includes(cards)} onClick={hiddenCards.toggle} onClickData={cards}>
            {capitalize(cards)}
        </SettingsMenuItem>
    )
}
VisibleCardsMenuItem.propTypes = {
    cards: hiddenCardsPropType,
    hiddenCards: stringsURLSearchQueryPropType,
}

function VisibleTagMenuItem({ tag, hiddenTags }) {
    return (
        <SettingsMenuItem active={!hiddenTags.includes(tag)} onClick={hiddenTags.toggle} onClickData={tag}>
            {tag}
        </SettingsMenuItem>
    )
}
VisibleTagMenuItem.propTypes = {
    tag: string,
    hiddenTags: stringsURLSearchQueryPropType,
}

function VisibleColumnMenuItem({ column, disabled, hiddenColumns, help, itemText }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : !hiddenColumns.includes(column)}
            disabled={disabled}
            disabledHelp={help}
            onClick={hiddenColumns.toggle}
            onClickData={column}
        >
            {itemText ?? capitalize(column).replaceAll("_", " ")}
        </SettingsMenuItem>
    )
}
VisibleColumnMenuItem.propTypes = {
    column: string,
    disabled: bool,
    hiddenColumns: stringsURLSearchQueryPropType,
    help: popupContentPropType,
    itemText: string,
}

function SortColumnMenuItem({ column, disabled, sortColumn, sortDirection, handleSort, help }) {
    let sortIndicator = null
    if (sortColumn.equals(column) && sortDirection.value) {
        // We use a triangle because the sort down and up icons are not at the same height
        const iconDirection = sortDirection.equals("ascending") ? "up" : "down"
        sortIndicator = (
            <Icon disabled={disabled} name={`triangle ${iconDirection}`} aria-label={`sorted ${sortDirection.value}`} />
        )
    }
    return (
        <SettingsMenuItem
            active={disabled ? false : sortColumn === column}
            disabled={disabled}
            disabledHelp={help}
            onClick={handleSort}
            onClickData={column}
        >
            {capitalize(column === "name" ? "metric" : column).replaceAll("_", " ")} <span>{sortIndicator}</span>
        </SettingsMenuItem>
    )
}
SortColumnMenuItem.propTypes = {
    column: string,
    disabled: bool,
    sortColumn: stringURLSearchQueryPropType,
    sortDirection: sortDirectionURLSearchQueryPropType,
    handleSort: func,
    help: popupContentPropType,
}

function NrOfDatesMenuItem({ nr, nrDates }) {
    return (
        <SettingsMenuItem active={nrDates.equals(nr)} onClick={nrDates.set} onClickData={nr}>
            {`${nr} ${pluralize("date", nr)}`}
        </SettingsMenuItem>
    )
}
NrOfDatesMenuItem.propTypes = {
    nr: number,
    nrDates: integerURLSearchQueryPropType,
}

function DateIntervalMenuItem({ nr, dateInterval, disabled, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : dateInterval.equals(nr)}
            disabled={disabled}
            disabledHelp={help}
            onClick={dateInterval.set}
            onClickData={nr}
        >
            {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
        </SettingsMenuItem>
    )
}
DateIntervalMenuItem.propTypes = {
    nr: number,
    dateInterval: integerURLSearchQueryPropType,
    disabled: bool,
    help: popupContentPropType,
}

function SortOrderMenuItem({ disabled, order, sortOrder, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : sortOrder.equals(order)}
            disabled={disabled}
            disabledHelp={help}
            onClick={sortOrder.set}
            onClickData={order}
        >
            {capitalize(order)}
        </SettingsMenuItem>
    )
}
SortOrderMenuItem.propTypes = {
    disabled: bool,
    order: sortDirectionPropType,
    sortOrder: sortDirectionURLSearchQueryPropType,
    help: popupContentPropType,
}

function MetricMenuItem({ hide, metricsToHide }) {
    return (
        <SettingsMenuItem active={metricsToHide.equals(hide)} onClick={metricsToHide.set} onClickData={hide}>
            {
                {
                    none: "All metrics",
                    no_action_needed: "Metrics requiring action",
                    all: "No metrics",
                }[hide]
            }
        </SettingsMenuItem>
    )
}
MetricMenuItem.propTypes = {
    hide: metricsToHidePropType,
    metricsToHide: metricsToHideURLSearchQueryPropType,
}

function IssueAttributeMenuItem({ help, issueAttributeName, issueAttribute }) {
    return (
        <SettingsMenuItem
            active={issueAttribute.value}
            help={help}
            onClick={issueAttribute.set}
            onClickData={!issueAttribute.value}
        >
            {issueAttributeName}
        </SettingsMenuItem>
    )
}
IssueAttributeMenuItem.propTypes = {
    help: popupContentPropType,
    issueAttributeName: string,
    issueAttribute: boolURLSearchQueryPropType,
}
