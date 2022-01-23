import React from 'react';
import { Button, Grid, Menu, Segment } from 'semantic-ui-react';
import { pluralize } from "../utils";
import './ViewPanel.css';

export function ViewPanel({
    clearVisibleDetailsTabs,
    dateInterval,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    nrDates,
    setDateInterval,
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
                                onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}
                                inverted
                            >
                                {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
                            </Button>
                        </Grid.Column>
                    </Grid.Row>
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
                <Menu text vertical inverted size="large">
                    <Menu.Item>
                        <Menu.Header>Columns</Menu.Header>
                        <Menu.Menu>
                            <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        </Menu.Menu>
                    </Menu.Item>
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Menu text vertical inverted size="large">
                    <Menu.Item>
                        <Menu.Header>Number of dates</Menu.Header>
                        <Menu.Menu>
                            {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                                <div key={nr} onKeyPress={(event) => { event.preventDefault(); setNrDates(nr) }} tabIndex={0}>
                                    <Menu.Item active={nr === nrDates} onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
                                </div>
                            )}
                        </Menu.Menu>
                    </Menu.Item>
                </Menu>
            </Segment>
            <Segment inverted color="black">
                <Menu text vertical inverted size="large">
                    <Menu.Item>
                        <Menu.Header>Time between dates</Menu.Header>
                        <Menu.Menu>
                            <DateIntervalMenuItem key={1} nr={1} dateInterval={dateInterval} setDateInterval={setDateInterval} />
                            {[7, 14, 21, 28].map((nr) => <DateIntervalMenuItem key={nr} nr={nr} dateInterval={dateInterval} setDateInterval={setDateInterval} />
                            )}
                        </Menu.Menu>
                    </Menu.Item>
                </Menu>
            </Segment>
        </Segment.Group>
    )
}

function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); toggleHiddenColumn(column) }} tabIndex={0}>
            <Menu.Item onClick={() => toggleHiddenColumn(column)}>
                {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
            </Menu.Item>
        </div>
    )
}

function DateIntervalMenuItem({ nr, dateInterval, setDateInterval }) {
    return (
        <div onKeyPress={(event) => { event.preventDefault(); setDateInterval(nr) }} tabIndex={0}>
            <Menu.Item key={nr} active={nr === dateInterval} onClick={() => setDateInterval(nr)}>
                {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
            </Menu.Item>
        </div>
    )
}