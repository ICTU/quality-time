import React from 'react';
import { Button, Grid, Header, Menu, Segment } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { capitalize, pluralize } from "../utils";
import './ViewPanel.css';

const activeColor = "grey"

export function ViewPanel({
    settings,
    setSettings,
    toggleHiddenColumn,
    postSettings,
    defaultSettings,
    handleSort
}) {
    const multipleDateColumns = settings.nr_dates > 1
    const oneDateColumn =  settings.nr_dates === 1
    settings.hidden_columns = settings.hidden_columns ?? [];

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
                            <Button
                                disabled={settings.tabs?.length === 0}
                                onClick={() => setSettings({tabs: []})}
                                inverted
                            >
                                Collapse all metrics
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <Button
                                onClick={() => {
                                    setSettings(defaultSettings)
                                }}
                                inverted
                            >
                                Reset all settings
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <Button
                                onClick={() => postSettings(settings)}
                                inverted
                            >
                                Save settings
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Dark/light mode</Header>
                <Menu vertical inverted size="small">
                    <UIModeMenuItem mode={null} uiMode={settings.ui_mode} setUIMode={(uiMode) => setSettings({ui_mode: uiMode})} />
                    <UIModeMenuItem mode="dark" uiMode={settings.ui_mode} setUIMode={(uiMode) => setSettings({ui_mode: uiMode})} />
                    <UIModeMenuItem mode="light" uiMode={settings.ui_mode} setUIMode={(uiMode) => setSettings({ui_mode: uiMode})} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible metrics</Header>
                <Menu vertical inverted size="small">
                    <MetricMenuItem 
                        hide={true}
                        hideMetricsNotRequiringAction={settings.hide_metrics_not_requiring_action}
                        setHideMetricsNotRequiringAction={(setHideMetricsNotRequiringAction) => setSettings({hide_metrics_not_requiring_action: setHideMetricsNotRequiringAction})} />
                    <MetricMenuItem
                        hide={false}
                        hideMetricsNotRequiringAction={settings.hide_metrics_not_requiring_action}
                        setHideMetricsNotRequiringAction={(setHideMetricsNotRequiringAction) => setSettings({hide_metrics_not_requiring_action: setHideMetricsNotRequiringAction})} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible columns</Header>
                <Menu vertical inverted size="small">
                    <VisibleColumnMenuItem column="trend" disabled={multipleDateColumns} hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="status" disabled={multipleDateColumns} hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="measurement" disabled={multipleDateColumns} hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="target" disabled={multipleDateColumns} hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="unit" hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="source" hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="comment" hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="issues" hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="tags" hiddenColumns={settings.hidden_columns} toggleHiddenColumn={toggleHiddenColumn} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Sort column</Header>
                <Menu vertical inverted size="small">
                    <SortColumnMenuItem column="name" sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="status" disabled={multipleDateColumns || settings.hidden_columns.includes("status")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="measurement" disabled={multipleDateColumns || settings.hidden_columns.includes("measurement")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="target" disabled={multipleDateColumns || settings.hidden_columns.includes("target")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="unit" disabled={settings.hidden_columns.includes("unit")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="source" disabled={settings.hidden_columns.includes("source")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="comment" disabled={settings.hidden_columns.includes("comment")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="issues" disabled={settings.hidden_columns.includes("issues")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                    <SortColumnMenuItem column="tags" disabled={settings.hidden_columns.includes("tags")} sortColumn={settings.sort_column} sortDirection={settings.sort_direction} handleSort={handleSort} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Number of dates</Header>
                <Menu vertical inverted size="small">
                    {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                        <div key={nr} onKeyPress={(event) => { event.preventDefault(); setSettings({nr_dates: nr}) }} tabIndex={0}>
                            <Menu.Item active={nr === settings.nr_dates} color={activeColor} onClick={() => setSettings({nr_dates: nr})}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
                        </div>
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Time between dates</Header>
                <Menu vertical inverted size="small">
                    <DateIntervalMenuItem key={1} nr={1} dateInterval={settings.dateInterval} disabled={oneDateColumn} setDateInterval={(dateInterval) => setSettings({date_interval: dateInterval})} />
                    {[7, 14, 21, 28].map((nr) =>
                        <DateIntervalMenuItem key={nr} nr={nr} dateInterval={settings.dateInterval} disabled={oneDateColumn} setDateInterval={(dateInterval) => setSettings({date_interval: dateInterval})} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Date order</Header>
                <Menu vertical inverted size="small">
                    <SortOrderMenuItem disabled={oneDateColumn} order="ascending" sortOrder={settings.date_order} setSortOrder={(dateOrder) => setSettings({date_order: dateOrder})} />
                    <SortOrderMenuItem disabled={oneDateColumn} order="descending" sortOrder={settings.date_order} setSortOrder={(dateOrder) => setSettings({date_order: dateOrder})} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible issue details</Header>
                <Menu vertical inverted size="small">
                    <IssueAttributeMenuItem
                        issueAttributeName="Summary"
                        issueAttribute={settings.show_issue_summary}
                        setIssueAttribute={(showIssueSummary) => setSettings({show_issue_summary: showIssueSummary})}
                        help="Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Creation date"
                        issueAttribute={settings.show_issue_creation_date}
                        setIssueAttribute={(showIssueCreationDate => setSettings({show_issue_creation_date: showIssueCreationDate}))}
                        help="Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Update date"
                        issueAttribute={settings.show_issue_update_date}
                        setIssueAttribute={(showIssueUpdateDate) => setSettings({show_issue_update_date: showIssueUpdateDate})}
                        help="Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Due date"
                        issueAttribute={settings.show_issue_due_date}
                        setIssueAttribute={(showIssueDueDate) => setSettings({show_issue_due_date: showIssueDueDate})}
                        help="Next to the issue status, also show the due date of issues. Note: the popup over the issue always shows the due date, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Release"
                        issueAttribute={settings.show_issue_release}
                        setIssueAttribute={(showIssueRelease) => setSettings({show_issue_release: showIssueRelease})}
                        help="Next to the issue status, also show the release issues are assigned to. Note: the popup over the issue always shows the release, if the issue has one, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Sprint"
                        issueAttribute={settings.show_issue_sprint}
                        setIssueAttribute={(showIssueSprint) => setSettings({show_issue_sprint: showIssueSprint})}
                        help="Next to the issue status, also show the sprint issues are assigned to. Note: the popup over the issue always shows the sprint, if the issue has one, regardless of this setting."
                    />
                </Menu>
            </Segment>
        </Segment.Group>
    )
}


function VisibleColumnMenuItem({ column, disabled, hiddenColumns, toggleHiddenColumn }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); toggleHiddenColumn(column) }} tabIndex={0}>
            <Menu.Item active={disabled ? false : !hiddenColumns?.includes(column)} color={activeColor} disabled={disabled} onClick={() => toggleHiddenColumn(column)}>
                {capitalize(column)}
            </Menu.Item>
        </div>
    )
}

function SortColumnMenuItem({ column, disabled, sortColumn, sortDirection, handleSort }) {
    const active = disabled ? false : sortColumn === column;
    let sortIndicator = null;
    if (sortColumn === column && sortDirection) {
        // We use a triangle because the sort down and up icons are not at the same height
        const iconDirection = sortDirection === "ascending" ? "up" : "down"
        sortIndicator = <Icon disabled={disabled} name={`triangle ${iconDirection}`} aria-label={`sorted ${sortDirection}`} />
    }
    return (
        <div onKeyPress={(event) => { event.preventDefault(); if (!disabled) { handleSort(column) } }} tabIndex={0}>
            <Menu.Item active={active} color={activeColor} disabled={disabled} onClick={() => handleSort(column)}>
                {capitalize(column === "name" ? "metric" : column)} <span>{sortIndicator}</span>
            </Menu.Item>
        </div>
    )
}

function DateIntervalMenuItem({ nr, dateInterval, disabled, setDateInterval }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setDateInterval(nr) }} tabIndex={0}>
            <Menu.Item key={nr} active={disabled ? false : nr === dateInterval} color={activeColor} disabled={disabled} onClick={() => setDateInterval(nr)}>
                {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
            </Menu.Item>
        </div>
    )
}

function SortOrderMenuItem({ disabled, order, sortOrder, setSortOrder }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setSortOrder(order) }} tabIndex={0}>
            <Menu.Item active={disabled ? false : sortOrder === order} color={activeColor} disabled={disabled} onClick={() => setSortOrder(order)}>
                {capitalize(order)}
            </Menu.Item>
        </div>
    )
}

function MetricMenuItem({ hide, hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setHideMetricsNotRequiringAction(hide) }} tabIndex={0}>
            <Menu.Item active={hideMetricsNotRequiringAction === hide} color={activeColor} onClick={() => setHideMetricsNotRequiringAction(hide)}>
                {hide ? 'Metrics requiring action' : 'All metrics'}
            </Menu.Item>
        </div>
    )
}

function UIModeMenuItem({ mode, uiMode, setUIMode }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setUIMode(mode) }} tabIndex={0}>
            <Menu.Item color={activeColor} active={mode === uiMode} onClick={() => setUIMode(mode)}>
                {{ null: "Follow OS setting", "dark": "Dark mode", "light": "Light mode" }[mode]}
            </Menu.Item>
        </div>
    )
}

function IssueAttributeMenuItem({ help, issueAttributeName, issueAttribute, setIssueAttribute }) {
    return (
        <Popup
            content={help}
            inverted
            position="left center"
            trigger={
                <div onKeyPress={(event) => { event.preventDefault(); setIssueAttribute(!issueAttribute) }} tabIndex={0}>
                    <Menu.Item color={activeColor} active={issueAttribute} onClick={() => setIssueAttribute(!issueAttribute)} >
                        {issueAttributeName}
                    </Menu.Item>
                </div>
            }
        />
    )
}
