import React from 'react';
import PropTypes from 'prop-types';
import { Button, Grid, Header, Menu, Segment } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { datePropType, issueSettingsPropType, sortDirectionPropType, uiModePropType } from '../sharedPropTypes';
import { capitalize, pluralize } from "../utils";
import './ViewPanel.css';

const activeColor = "grey"

export function ViewPanel({
    clearHiddenColumns,
    clearHiddenTags,
    clearVisibleDetailsTabs,
    dateInterval,
    dateOrder,
    handleDateChange,
    handleSort,
    hiddenColumns,
    hiddenTags,
    hideMetricsNotRequiringAction,
    issueSettings,
    nrDates,
    reportDate,
    setDateInterval,
    setDateOrder,
    setHideMetricsNotRequiringAction,
    setNrDates,
    setShowIssueCreationDate,
    setShowIssueSummary,
    setShowIssueUpdateDate,
    setShowIssueDueDate,
    setShowIssueRelease,
    setShowIssueSprint,
    setUIMode,
    sortColumn,
    sortDirection,
    tags,
    toggleHiddenColumn,
    toggleHiddenTag,
    uiMode,
    visibleDetailsTabs
}) {
    const multipleDateColumns = nrDates > 1
    const oneDateColumn = nrDates === 1
    const menuProps = { compact: true, vertical: true, inverted: true, secondary: true }
    const dateIntervalMenuItemProps = {
        dateInterval: dateInterval,
        disabled: oneDateColumn,
        help: "The date interval can only be changed when at least two dates are shown",
        setDateInterval: setDateInterval
    }
    const metricMenuItemProps = {
        hideMetricsNotRequiringAction: hideMetricsNotRequiringAction,
        setHideMetricsNotRequiringAction: setHideMetricsNotRequiringAction
    }
    const sortColumnMenuItemProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    const sortOrderMenuItemProps = {
        disabled: oneDateColumn,
        help: "The date order can only be changed when at least two dates are shown",
        setSortOrder: setDateOrder,
        sortOrder: dateOrder,
    }
    const visibleColumnMenuItemProps = { hiddenColumns: hiddenColumns, toggleHiddenColumn: toggleHiddenColumn }
    hiddenColumns = hiddenColumns ?? [];
    visibleDetailsTabs = visibleDetailsTabs ?? [];
    return (
        <Segment.Group
            horizontal
            className='equal width'
            style={{ margin: "0px", border: "0px" }}
        >
            <Segment inverted color="black">
                <Grid padded>
                    <Grid.Row>
                        <Grid.Column>
                            <ResetAllSettingsButton
                                clearHiddenColumns={clearHiddenColumns}
                                clearHiddenTags={clearHiddenTags}
                                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                                dateInterval={dateInterval}
                                dateOrder={dateOrder}
                                handleDateChange={handleDateChange}
                                handleSort={handleSort}
                                hiddenColumns={hiddenColumns}
                                hiddenTags={hiddenTags}
                                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                                issueSettings={issueSettings}
                                nrDates={nrDates}
                                reportDate={reportDate}
                                setDateInterval={setDateInterval}
                                setDateOrder={setDateOrder}
                                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                                setNrDates={setNrDates}
                                setShowIssueCreationDate={setShowIssueCreationDate}
                                setShowIssueSummary={setShowIssueSummary}
                                setShowIssueUpdateDate={setShowIssueUpdateDate}
                                setShowIssueDueDate={setShowIssueDueDate}
                                setShowIssueRelease={setShowIssueRelease}
                                setShowIssueSprint={setShowIssueSprint}
                                setUIMode={setUIMode}
                                sortColumn={sortColumn}
                                sortDirection={sortDirection}
                                uiMode={uiMode}
                                visibleDetailsTabs={visibleDetailsTabs}
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Dark/light mode</Header>
                <Menu {...menuProps}>
                    <UIModeMenuItem mode={null} uiMode={uiMode} setUIMode={setUIMode} />
                    <UIModeMenuItem mode="dark" uiMode={uiMode} setUIMode={setUIMode} />
                    <UIModeMenuItem mode="light" uiMode={uiMode} setUIMode={setUIMode} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible metrics</Header>
                <Menu {...menuProps}>
                    <MetricMenuItem hide={false} {...metricMenuItemProps} />
                    <MetricMenuItem hide={true} {...metricMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible tags</Header>
                <Menu style={{ maxHeight: "450px", overflow: "auto" }} {...menuProps}>
                    {(tags ?? []).map((tag) =>
                        <VisibleTagMenuItem key={tag} tag={tag} hiddenTags={hiddenTags} toggleHiddenTag={toggleHiddenTag} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible columns</Header>
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
                        column="overrun"
                        disabled={nrDates === 1}
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
                        disabled={multipleDateColumns || hiddenColumns.includes("status")}
                        help="The status column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="measurement"
                        disabled={multipleDateColumns || hiddenColumns.includes("measurement")}
                        help="The measurement column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="target"
                        disabled={multipleDateColumns || hiddenColumns.includes("target")}
                        help="The target column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="unit"
                        disabled={hiddenColumns.includes("unit")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="source"
                        disabled={hiddenColumns.includes("source")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="time_left"
                        disabled={hiddenColumns.includes("time_left")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="overrun"
                        disabled={nrDates === 1 || hiddenColumns.includes("overrun")}
                        help="The overrun column can only be selected for sorting when it is visible"
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="comment"
                        disabled={hiddenColumns.includes("comment")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="issues"
                        disabled={hiddenColumns.includes("issues")}
                        {...sortColumnMenuItemProps}
                    />
                    <SortColumnMenuItem
                        column="tags"
                        disabled={hiddenColumns.includes("tags")}
                        {...sortColumnMenuItemProps}
                    />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Number of dates</Header>
                <Menu {...menuProps}>
                    {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                        <NrOfDatesMenuItem key={nr} nr={nr} nrDates={nrDates} setNrDates={setNrDates} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Time between dates</Header>
                <Menu {...menuProps}>
                    <DateIntervalMenuItem key={1} nr={1} {...dateIntervalMenuItemProps} />
                    {[7, 14, 21, 28].map((nr) =>
                        <DateIntervalMenuItem key={nr} nr={nr} {...dateIntervalMenuItemProps} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Date order</Header>
                <Menu {...menuProps}>
                    <SortOrderMenuItem order="ascending" {...sortOrderMenuItemProps} />
                    <SortOrderMenuItem order="descending" {...sortOrderMenuItemProps} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible issue details</Header>
                <Menu {...menuProps}>
                    <IssueAttributeMenuItem
                        issueAttributeName="Summary"
                        issueAttribute={issueSettings?.showIssueSummary}
                        setIssueAttribute={setShowIssueSummary}
                        help="Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Creation date"
                        issueAttribute={issueSettings?.showIssueCreationDate}
                        setIssueAttribute={setShowIssueCreationDate}
                        help="Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Update date"
                        issueAttribute={issueSettings?.showIssueUpdateDate}
                        setIssueAttribute={setShowIssueUpdateDate}
                        help="Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Due date"
                        issueAttribute={issueSettings?.showIssueDueDate}
                        setIssueAttribute={setShowIssueDueDate}
                        help="Next to the issue status, also show the due date of issues. Note: the popup over the issue always shows the due date, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Release"
                        issueAttribute={issueSettings?.showIssueRelease}
                        setIssueAttribute={setShowIssueRelease}
                        help="Next to the issue status, also show the release issues are assigned to. Note: the popup over the issue always shows the release, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Sprint"
                        issueAttribute={issueSettings?.showIssueSprint}
                        setIssueAttribute={setShowIssueSprint}
                        help="Next to the issue status, also show the sprint issues are assigned to. Note: the popup over the issue always shows the sprint, if the issue has one, regardless of this setting."
                    />
                </Menu>
            </Segment>
        </Segment.Group>
    )
}
ViewPanel.propTypes = {
    toggleHiddenColumn: PropTypes.func,
    toggleHiddenTag: PropTypes.func,
    ...ResetAllSettingsButton.propTypes,
}

function VisibleTagMenuItem({ tag, hiddenTags, toggleHiddenTag }) {
    return (
        <SettingsMenuItem
            active={!hiddenTags?.includes(tag)}
            onClick={toggleHiddenTag}
            onClickData={tag}
        >
            {tag}
        </SettingsMenuItem>
    )
}
VisibleTagMenuItem.propTypes = {
    tag: PropTypes.string,
    hiddenTags: PropTypes.arrayOf(PropTypes.string),
    toggleHiddenTag: PropTypes.func
}

function VisibleColumnMenuItem({ column, disabled, hiddenColumns, toggleHiddenColumn, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : !hiddenColumns?.includes(column)}
            disabled={disabled}
            disabledHelp={help}
            onClick={toggleHiddenColumn}
            onClickData={column}
        >
            {capitalize(column).replaceAll('_', ' ')}
        </SettingsMenuItem>
    )
}
VisibleColumnMenuItem.propTypes = {
    column: PropTypes.string,
    disabled: PropTypes.bool,
    hiddenColumns: PropTypes.arrayOf(PropTypes.string),
    toggleHiddenColumn: PropTypes.func,
    help: PropTypes.string
}

function SortColumnMenuItem({ column, disabled, sortColumn, sortDirection, handleSort, help }) {
    let sortIndicator = null;
    if (sortColumn === column && sortDirection) {
        // We use a triangle because the sort down and up icons are not at the same height
        const iconDirection = sortDirection === "ascending" ? "up" : "down"
        sortIndicator = <Icon disabled={disabled} name={`triangle ${iconDirection}`} aria-label={`sorted ${sortDirection}`} />
    }
    return (
        <SettingsMenuItem
            active={disabled ? false : sortColumn === column}
            disabled={disabled}
            disabledHelp={help}
            onClick={handleSort}
            onClickData={column}
        >
            {capitalize(column === "name" ? "metric" : column).replaceAll('_', ' ')} <span>{sortIndicator}</span>
        </SettingsMenuItem>
    )
}
SortColumnMenuItem.propTypes = {
    column: PropTypes.string,
    disabled: PropTypes.bool,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    handleSort: PropTypes.func,
    help: PropTypes.string
}

function NrOfDatesMenuItem({ nr, nrDates, setNrDates }) {
    return (
        <SettingsMenuItem
            active={nr === nrDates}
            onClick={setNrDates}
            onClickData={nr}
        >
            {`${nr} ${pluralize("date", nr)}`}
        </SettingsMenuItem>
    )
}
NrOfDatesMenuItem.propTypes = {
    nr: PropTypes.number,
    nrDates: PropTypes.number,
    setNrDates: PropTypes.func
}

function DateIntervalMenuItem({ nr, dateInterval, disabled, setDateInterval, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : nr === dateInterval}
            disabled={disabled}
            disabledHelp={help}
            onClick={setDateInterval}
            onClickData={nr}
        >
            {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
        </SettingsMenuItem>
    )
}
DateIntervalMenuItem.propTypes = {
    nr: PropTypes.number,
    dateInterval: PropTypes.number,
    disabled: PropTypes.bool,
    setDateInterval: PropTypes.func,
    help: PropTypes.string
}

function SortOrderMenuItem({ disabled, order, sortOrder, setSortOrder, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : sortOrder === order}
            disabled={disabled}
            disabledHelp={help}
            onClick={setSortOrder}
            onClickData={order}
        >
            {capitalize(order)}
        </SettingsMenuItem>
    )
}
SortOrderMenuItem.propTypes = {
    disabled: PropTypes.bool,
    order: sortDirectionPropType,
    sortOrder: sortDirectionPropType,
    setSortOrder: PropTypes.func,
    help: PropTypes.string
}

function MetricMenuItem({ hide, hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction }) {
    return (
        <SettingsMenuItem
            active={hideMetricsNotRequiringAction === hide}
            onClick={setHideMetricsNotRequiringAction}
            onClickData={hide}
        >
            {hide ? 'Metrics requiring action' : 'All metrics'}
        </SettingsMenuItem>
    )
}
MetricMenuItem.propTypes = {
    hide: PropTypes.bool,
    hideMetricsNotRequiringAction: PropTypes.bool,
    setHideMetricsNotRequiringAction: PropTypes.func
}

function UIModeMenuItem({ mode, uiMode, setUIMode }) {
    return (
        <SettingsMenuItem
            active={mode === uiMode}
            onClick={setUIMode}
            onClickData={mode}
        >
            {{ null: "Follow OS setting", "dark": "Dark mode", "light": "Light mode" }[mode]}
        </SettingsMenuItem>
    )
}
UIModeMenuItem.propTypes = {
    mode: uiModePropType,
    uiMode: uiModePropType,
    setUIMode: PropTypes.func
}

function IssueAttributeMenuItem({ help, issueAttributeName, issueAttribute, setIssueAttribute }) {
    return (
        <SettingsMenuItem
            active={issueAttribute}
            help={help}
            onClick={setIssueAttribute}
            onClickData={!issueAttribute}
        >
            {issueAttributeName}
        </SettingsMenuItem>
    )
}
IssueAttributeMenuItem.propTypes = {
    help: PropTypes.string,
    issueAttributeName: PropTypes.string,
    issueAttribute: PropTypes.bool,
    setIssueAttribute: PropTypes.func
}

function SettingsMenuItem({ active, children, disabled, disabledHelp, help, onClick, onClickData }) {
    // A menu item that can can show help when disabled so users can see why the menu item is disabled
    const props = {
        active: active,
        color: activeColor,
        disabled: disabled,
        onBeforeInput: (event) => { event.preventDefault(); if (!disabled) { onClick(onClickData) } },  // Uncovered, see https://github.com/testing-library/react-testing-library/issues/1152
        onClick: () => onClick(onClickData),
        tabIndex: 0
    }
    if (help || (disabledHelp && disabled)) {
        props["style"] = { marginLeft: 0, marginRight: 0, marginBottom: 5 }  // Compensate for the span
        return (
            <Popup
                content={disabledHelp || help}
                inverted
                position="left center"
                // We need a span here to prevent the popup from becoming disabled when the menu item is disabled:
                trigger={<span><Menu.Item {...props}>{children}</Menu.Item></span>}
            />
        )
    }
    return <Menu.Item {...props} >{children}</Menu.Item>
}
SettingsMenuItem.propTypes = {
    active: PropTypes.bool,
    children: PropTypes.oneOfType([PropTypes.array, PropTypes.string]),
    disabled: PropTypes.bool,
    disabledHelp: PropTypes.string,
    help: PropTypes.string,
    onClick: PropTypes.func,
    onClickData: PropTypes.oneOfType([PropTypes.bool, PropTypes.number, PropTypes.string])
}

function ResetAllSettingsButton(
    {
        clearHiddenColumns,
        clearHiddenTags,
        clearVisibleDetailsTabs,
        dateInterval,
        dateOrder,
        handleDateChange,
        handleSort,
        hiddenColumns,
        hiddenTags,
        hideMetricsNotRequiringAction,
        issueSettings,
        nrDates,
        reportDate,
        setDateInterval,
        setDateOrder,
        setHideMetricsNotRequiringAction,
        setNrDates,
        setShowIssueCreationDate,
        setShowIssueSummary,
        setShowIssueUpdateDate,
        setShowIssueDueDate,
        setShowIssueRelease,
        setShowIssueSprint,
        setUIMode,
        sortColumn,
        sortDirection,
        uiMode,
        visibleDetailsTabs
    }
) {
    return (
        <Button
            disabled={
                visibleDetailsTabs?.length === 0 &&
                !hideMetricsNotRequiringAction &&
                hiddenColumns?.length === 0 &&
                hiddenTags?.length === 0 &&
                nrDates === 1 &&
                dateInterval === 7 &&
                dateOrder === "descending" &&
                !issueSettings.showIssueCreationDate &&
                !issueSettings.showIssueSummary &&
                !issueSettings.showIssueUpdateDate &&
                !issueSettings.showIssueDueDate &&
                !issueSettings.showIssueRelease &&
                !issueSettings.showIssueSprint &&
                reportDate === null &&
                sortColumn === null &&
                sortDirection === "ascending" &&
                uiMode === null
            }
            onClick={() => {
                clearVisibleDetailsTabs();
                setHideMetricsNotRequiringAction(false);
                clearHiddenColumns();
                clearHiddenTags();
                handleDateChange(null);
                handleSort(null);
                setNrDates(1);
                setDateInterval(7);
                setDateOrder("descending");
                setShowIssueCreationDate(false);
                setShowIssueSummary(false);
                setShowIssueUpdateDate(false);
                setShowIssueDueDate(false);
                setShowIssueRelease(false);
                setShowIssueSprint(false);
                setUIMode(null);
            }}
            inverted
        >
            Reset all settings
        </Button>
    )
}
ResetAllSettingsButton.propTypes = {
    clearHiddenColumns: PropTypes.func,
    clearHiddenTags: PropTypes.func,
    clearVisibleDetailsTabs: PropTypes.func,
    dateInterval: PropTypes.number,
    dateOrder: sortDirectionPropType,
    handleDateChange: PropTypes.func,
    handleSort: PropTypes.func,
    hiddenColumns: PropTypes.arrayOf(PropTypes.string),
    hiddenTags: PropTypes.arrayOf(PropTypes.string),
    hideMetricsNotRequiringAction: PropTypes.bool,
    issueSettings: issueSettingsPropType,
    nrDates: PropTypes.number,
    reportDate: datePropType,
    setDateInterval: PropTypes.func,
    setDateOrder: PropTypes.func,
    setHideMetricsNotRequiringAction: PropTypes.func,
    setNrDates: PropTypes.func,
    setShowIssueCreationDate: PropTypes.func,
    setShowIssueSummary: PropTypes.func,
    setShowIssueUpdateDate: PropTypes.func,
    setShowIssueDueDate: PropTypes.func,
    setShowIssueRelease: PropTypes.func,
    setShowIssueSprint: PropTypes.func,
    setUIMode: PropTypes.func,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    uiMode: uiModePropType,
    visibleDetailsTabs: PropTypes.arrayOf(PropTypes.string)
}
