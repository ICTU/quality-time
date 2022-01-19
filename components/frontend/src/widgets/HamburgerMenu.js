import React from 'react';
import { Icon, Menu, Popup } from 'semantic-ui-react';
import { pluralize } from "../utils";
import './HamburgerMenu.css';

export function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <Menu.Item onClick={() => toggleHiddenColumn(column)}>
            {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Menu.Item>
    )
}

export function HamburgerMenu({
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
        <Popup on={["click", "focus", "hover"]} hoverable position="bottom left" trigger={<Icon tabIndex="0" data-testid="HamburgerMenu" className="HamburgerMenu" name="sidebar" />}>
            <Menu text vertical>
                <Menu.Item key="collapse_metrics" disabled={visibleDetailsTabs.length === 0} onClick={() => clearVisibleDetailsTabs()}>
                    Collapse all metrics
                </Menu.Item>
                <Menu.Item key="hide_metrics" onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}>
                    {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
                </Menu.Item>
                <Menu.Item key="hide_columns">
                    <Menu.Header>Toggle visibility of columns</Menu.Header>
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
                <Menu.Item key="nr_dates">
                    <Menu.Header>Number of dates</Menu.Header>
                    <Menu.Menu>
                        {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                            <Menu.Item key={nr} active={nr === nrDates} onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
                        )}
                    </Menu.Menu>
                </Menu.Item>
                <Menu.Item key="time_between_dates">
                    <Menu.Header>Time between dates</Menu.Header>
                    <Menu.Menu>
                        <Menu.Item key={1} active={1 === dateInterval} onClick={() => setDateInterval(1)}>1 day</Menu.Item>
                        {[7, 14, 21, 28].map((nr) =>
                            <Menu.Item key={nr} active={nr === dateInterval} onClick={() => setDateInterval(nr)}>{`${nr / 7} ${pluralize("week", nr / 7)}`}</Menu.Item>
                        )}
                    </Menu.Menu>
                </Menu.Item>
            </Menu>
        </Popup>
    )
}
