import React from 'react';
import { Button, Grid, Header, Menu, Segment } from 'semantic-ui-react';
import { capitalize, pluralize } from "../utils";
import './ViewPanel.css';

const activeColor = "grey"

export function ViewPanel({
    clearHiddenColumns,
    clearVisibleDetailsTabs,
    dateInterval,
    dateOrder,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    nrDates,
    setDateInterval,
    setDateOrder,
    setHideMetricsNotRequiringAction,
    setNrDates,
    setSortColumn,
    setSortDirection,
    sortColumn,
    sortDirection,
    toggleHiddenColumn,
    visibleDetailsTabs
}) {
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
                                disabled={visibleDetailsTabs.length === 0}
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
                                    visibleDetailsTabs.length === 0 &&
                                    !hideMetricsNotRequiringAction &&
                                    hiddenColumns.length === 0 &&
                                    nrDates === 1 &&
                                    dateInterval === 7 &&
                                    dateOrder === "descending" &&
                                    sortColumn === null &&
                                    sortDirection === "ascending"
                                }
                                onClick={() => {
                                    clearVisibleDetailsTabs();
                                    setHideMetricsNotRequiringAction(false);
                                    clearHiddenColumns();
                                    setNrDates(1);
                                    setDateInterval(7);
                                    setDateOrder("descending");
                                    setSortColumn(null);
                                    setSortDirection("ascending")
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
                <Header size='small'>Visible metrics</Header>
                <Menu vertical inverted size="small">
                    <MetricMenuItem hide={true} hideMetricsNotRequiringAction={hideMetricsNotRequiringAction} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />
                    <MetricMenuItem hide={false} hideMetricsNotRequiringAction={hideMetricsNotRequiringAction} setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Visible columns</Header>
                <Menu vertical inverted size="small">
                    <VisibleColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <VisibleColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
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
                    <SortColumnMenuItem column="name" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="status" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="measurement" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="target" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="unit" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="source" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="comment" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="issues" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                    <SortColumnMenuItem column="tags" sortColumn={sortColumn} setSortColumn={setSortColumn} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Sort direction</Header>
                <Menu vertical inverted size="small">
                    <SortOrderMenuItem order="ascending" sortOrder={sortDirection} setSortOrder={setSortDirection} />
                    <SortOrderMenuItem order="descending" sortOrder={sortDirection} setSortOrder={setSortDirection} />
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
                    <DateIntervalMenuItem key={1} nr={1} dateInterval={dateInterval} setDateInterval={setDateInterval} />
                    {[7, 14, 21, 28].map((nr) =>
                        <DateIntervalMenuItem key={nr} nr={nr} dateInterval={dateInterval} setDateInterval={setDateInterval} />
                    )}
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Date order</Header>
                <Menu vertical inverted size="small">
                    <SortOrderMenuItem order="ascending" sortOrder={dateOrder} setSortOrder={setDateOrder} />
                    <SortOrderMenuItem order="descending" sortOrder={dateOrder} setSortOrder={setDateOrder} />
                </Menu>
            </Segment>
        </Segment.Group>
    )
}

function VisibleColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); toggleHiddenColumn(column) }} tabIndex={0}>
            <Menu.Item color={activeColor} active={!hiddenColumns.includes(column)} onClick={() => toggleHiddenColumn(column)}>
                {capitalize(column)}
            </Menu.Item>
        </div>
    )
}

function SortColumnMenuItem({ column, sortColumn, setSortColumn }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setSortColumn(column) }} tabIndex={0}>
            <Menu.Item color={activeColor} active={sortColumn === column} onClick={() => setSortColumn(sortColumn === column ? null : column)}>
                {capitalize(column === "name" ? "metric" : column)}
            </Menu.Item>
        </div>
    )
}

function DateIntervalMenuItem({ nr, dateInterval, setDateInterval }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setDateInterval(nr) }} tabIndex={0}>
            <Menu.Item key={nr} active={nr === dateInterval} color={activeColor} onClick={() => setDateInterval(nr)}>
                {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
            </Menu.Item>
        </div>
    )
}

function SortOrderMenuItem({ order, sortOrder, setSortOrder }) {
    return (
        <div key={order} onKeyPress={(event) => { event.preventDefault(); setSortOrder(order) }} tabIndex={0}>
            <Menu.Item active={sortOrder === order} color={activeColor} onClick={() => setSortOrder(order)}>
                {capitalize(order)}
            </Menu.Item>
        </div>
    )
}

function MetricMenuItem({ hide, hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction }) {
    return (
        <div key={hide} onKeyPress={(event) => { event.preventDefault(); setHideMetricsNotRequiringAction(hide) }} tabIndex={0}>
            <Menu.Item active={hideMetricsNotRequiringAction === hide} color={activeColor} onClick={() => setHideMetricsNotRequiringAction(hide)}>
                {hide ? 'Metrics requiring action' : 'All metrics'}
            </Menu.Item>
        </div>
    )
}
