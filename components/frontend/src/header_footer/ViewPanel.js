import React from 'react';
import { Button, Grid, Header, Menu, Segment } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { capitalize, pluralize } from "../utils";
import './ViewPanel.css';

const activeColor = "grey"

export function ViewPanel({
    clearHiddenColumns,
    clearVisibleDetailsTabs,
    dateInterval,
    dateOrder,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    nrDates,
    setDateInterval,
    setDateOrder,
    setHideMetricsNotRequiringAction,
    setNrDates,
    setShowIssueCreationDate,
    setShowIssueSummary,
    setShowIssueUpdateDate,
    setUIMode,
    showIssueCreationDate,
    showIssueSummary,
    showIssueUpdateDate,
    sortColumn,
    sortDirection,
    toggleHiddenColumn,
    uiMode,
    visibleDetailsTabs
}) {
    const multipleDateColumns = nrDates > 1
    const oneDateColumn = nrDates === 1
    hiddenColumns = hiddenColumns ?? [];
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
                                disabled={visibleDetailsTabs?.length === 0}
                                onClick={() => clearVisibleDetailsTabs()}
                                inverted
                            >
                                Collapse all metrics
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <Button
                                disabled={
                                    visibleDetailsTabs?.length === 0 &&
                                    !hideMetricsNotRequiringAction &&
                                    hiddenColumns?.length === 0 &&
                                    nrDates === 1 &&
                                    dateInterval === 7 &&
                                    dateOrder === "descending" &&
                                    !showIssueCreationDate &&
                                    !showIssueSummary &&
                                    !showIssueUpdateDate &&
                                    sortColumn === null &&
                                    sortDirection === "ascending" &&
                                    uiMode === null
                                }
                                onClick={() => {
                                    clearVisibleDetailsTabs();
                                    setHideMetricsNotRequiringAction(false);
                                    clearHiddenColumns();
                                    handleSort(null);
                                    setNrDates(1);
                                    setDateInterval(7);
                                    setDateOrder("descending");
                                    setShowIssueCreationDate(false);
                                    setShowIssueSummary(false);
                                    setShowIssueUpdateDate(false);
                                    setUIMode(null);
                                }}
                                inverted
                            >
                                Reset all settings
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Dark/light mode</Header>
                <Menu vertical inverted size="small">
                    <UIModeMenuItem mode={null} uiMode={uiMode} setUIMode={setUIMode} />
                    <UIModeMenuItem mode="dark" uiMode={uiMode} setUIMode={setUIMode} />
                    <UIModeMenuItem mode="light" uiMode={uiMode} setUIMode={setUIMode} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible metrics</Header>
                <Menu vertical inverted size="small">
                    <MetricMenuItem hide={true} hideMetricsNotRequiringAction={hideMetricsNotRequiringAction} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />
                    <MetricMenuItem hide={false} hideMetricsNotRequiringAction={hideMetricsNotRequiringAction} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible columns</Header>
                <Menu vertical inverted size="small">
                    <VisibleColumnMenuItem column="trend" disabled={multipleDateColumns} hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="status" disabled={multipleDateColumns} hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="measurement" disabled={multipleDateColumns} hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="target" disabled={multipleDateColumns} hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="unit" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size="small">Sort column</Header>
                <Menu vertical inverted size="small">
                    <SortColumnMenuItem column="name" sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="status" disabled={multipleDateColumns || hiddenColumns.includes("status")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="measurement" disabled={multipleDateColumns || hiddenColumns.includes("measurement")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="target" disabled={multipleDateColumns || hiddenColumns.includes("target")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="unit" disabled={hiddenColumns.includes("unit")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="source" disabled={hiddenColumns.includes("source")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="comment" disabled={hiddenColumns.includes("comment")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="issues" disabled={hiddenColumns.includes("issues")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                    <SortColumnMenuItem column="tags" disabled={hiddenColumns.includes("tags")} sortColumn={sortColumn} sortDirection={sortDirection} handleSort={handleSort} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Number of dates</Header>
                <Menu vertical inverted size="small">
                    {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                        <div key={nr} onKeyPress={(event) => { event.preventDefault(); setNrDates(nr) }} tabIndex={0}>
                            <Menu.Item active={nr === nrDates} color={activeColor} onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
                        </div>
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Time between dates</Header>
                <Menu vertical inverted size="small">
                    <DateIntervalMenuItem key={1} nr={1} dateInterval={dateInterval} disabled={oneDateColumn} setDateInterval={setDateInterval} />
                    {[7, 14, 21, 28].map((nr) =>
                        <DateIntervalMenuItem key={nr} nr={nr} dateInterval={dateInterval} disabled={oneDateColumn} setDateInterval={setDateInterval} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Date order</Header>
                <Menu vertical inverted size="small">
                    <SortOrderMenuItem disabled={oneDateColumn} order="ascending" sortOrder={dateOrder} setSortOrder={setDateOrder} />
                    <SortOrderMenuItem disabled={oneDateColumn} order="descending" sortOrder={dateOrder} setSortOrder={setDateOrder} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible issue details</Header>
                <Menu vertical inverted size="small">
                    <IssueAttributeMenuItem
                        issueAttributeName="Summary"
                        issueAttribute={showIssueSummary}
                        setIssueAttribute={setShowIssueSummary}
                        help="Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Creation date"
                        issueAttribute={showIssueCreationDate}
                        setIssueAttribute={setShowIssueCreationDate}
                        help="Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
                    />
                    <IssueAttributeMenuItem
                        issueAttributeName="Update date"
                        issueAttribute={showIssueUpdateDate}
                        setIssueAttribute={setShowIssueUpdateDate}
                        help="Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
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
        sortIndicator = <Icon disabled={disabled} name={`triangle ${iconDirection}`} aria-label={`sort ${sortDirection}`} />
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
