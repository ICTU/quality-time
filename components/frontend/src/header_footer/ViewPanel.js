import React from 'react';
import { Button, Grid, Menu, Segment } from 'semantic-ui-react';
import { pluralize } from "../utils";

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
                                onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}
                                inverted
                            >
                                {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
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
                                <Menu.Item key={nr} active={nr === nrDates} onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
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
                            <Menu.Item key={1} active={1 === dateInterval} onClick={() => setDateInterval(1)}>1 day</Menu.Item>
                            {[7, 14, 21, 28].map((nr) =>
                                <Menu.Item key={nr} active={nr === dateInterval} onClick={() => setDateInterval(nr)}>{`${nr / 7} ${pluralize("week", nr / 7)}`}</Menu.Item>
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
        <Menu.Item onClick={() => toggleHiddenColumn(column)}>
            {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Menu.Item>
    )
}
