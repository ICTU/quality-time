import React from 'react';
import { Button, Grid, Header, Menu, Segment } from 'semantic-ui-react';
import { capitalize, pluralize } from "../utils";
import './ViewPanel.css';

export function ViewPanel({
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
    toggleHiddenColumn,
    visibleDetailsTabs
}) {
    return (
        <Segment.Group
            horizontal
            className='equal width'
            style={{
                border: "0px",
                left: "0px",
                margin: "0px",
                opacity: "0.98",
                position: "fixed",
                top: "64px",
                width: "100%",
                zIndex: 2,
            }}
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
                    <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Header size='small'>Number of dates</Header>
                <Menu vertical inverted size="small">
                    {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                        <div key={nr} onKeyPress={(event) => { event.preventDefault(); setNrDates(nr) }} tabIndex={0}>
                            <Menu.Item active={nr === nrDates} color="blue" onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
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
                    <DateOrderMenuItem order="ascending" dateOrder={dateOrder} setDateOrder={setDateOrder} />
                    <DateOrderMenuItem order="descending" dateOrder={dateOrder} setDateOrder={setDateOrder} />
                </Menu>
            </Segment>
        </Segment.Group>
    )
}

function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); toggleHiddenColumn(column) }} tabIndex={0}>
            <Menu.Item color="blue" active={!hiddenColumns.includes(column)} onClick={() => toggleHiddenColumn(column)}>
                {capitalize(column)}
            </Menu.Item>
        </div>
    )
}

function DateIntervalMenuItem({ nr, dateInterval, setDateInterval }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setDateInterval(nr) }} tabIndex={0}>
            <Menu.Item key={nr} active={nr === dateInterval} color="blue" onClick={() => setDateInterval(nr)}>
                {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
            </Menu.Item>
        </div>
    )
}

function DateOrderMenuItem({ order, dateOrder, setDateOrder }) {
    return (
        <div key={order} onKeyPress={(event) => { event.preventDefault(); setDateOrder(order) }} tabIndex={0}>
            <Menu.Item active={dateOrder === order} color="blue" onClick={() => setDateOrder(order)}>
                {capitalize(order)}
            </Menu.Item>
        </div>
    )
}

function MetricMenuItem({ hide, hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction }) {
    return (
        <div key={hide} onKeyPress={(event) => { event.preventDefault(); setHideMetricsNotRequiringAction(hide) }} tabIndex={0}>
            <Menu.Item active={hideMetricsNotRequiringAction === hide} color="blue" onClick={() => setHideMetricsNotRequiringAction(hide)}>
                {hide ? 'Metrics requiring action' : 'All metrics'}
            </Menu.Item>
        </div>
    )
}
