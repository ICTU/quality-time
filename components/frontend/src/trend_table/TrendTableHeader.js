import { Dropdown, Icon, Table } from "semantic-ui-react";
import { ColumnMenuItem, HamburgerMenu } from "../widgets/HamburgerMenu";
import { SortableTableHeaderCell } from '../widgets/SortableTableHeaderCell';
import { pluralize } from "../utils";

export function TrendTableHeader(
    {
        columnDates,
        extraHamburgerItems,
        handleSort,
        hiddenColumns,
        setTrendTableInterval,
        setTrendTableNrDates,
        sortColumn,
        sortDirection,
        toggleHiddenColumn,
        trendTableInterval,
        trendTableNrDates
    }) {
    const sortProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    return (
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell className="unsortable" textAlign="center">
                    <HamburgerMenu>
                        {extraHamburgerItems}
                        <Dropdown.Item key="columns">
                            <Icon name='dropdown' /><span className='text'>Toggle visibility of columns</span>
                            <Dropdown.Menu>
                                <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            </Dropdown.Menu>
                        </Dropdown.Item>
                        <Dropdown.Item key="nr_dates">
                            <Icon name='dropdown' /><span className='text'>Numer of dates</span>
                            <Dropdown.Menu>
                                {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                                    <Dropdown.Item key={nr} active={nr === trendTableNrDates} onClick={() => setTrendTableNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Dropdown.Item>
                                )}
                            </Dropdown.Menu>
                        </Dropdown.Item>
                        <Dropdown.Item key="time_between_dates">
                            <Icon name='dropdown' /><span className='text'>Time between dates</span>
                            <Dropdown.Menu>
                                <Dropdown.Item key={1} active={1 === trendTableInterval} onClick={() => setTrendTableInterval(1)}>1 day</Dropdown.Item>
                                {[7, 14, 21, 28].map((nr) =>
                                    <Dropdown.Item key={nr} active={nr === trendTableInterval} onClick={() => setTrendTableInterval(nr)}>{`${nr / 7} ${pluralize("week", nr / 7)}`}</Dropdown.Item>
                                )}
                            </Dropdown.Menu>
                        </Dropdown.Item>
                    </HamburgerMenu>
                </Table.HeaderCell>
                <SortableTableHeaderCell column='name' label='Metric' {...sortProps} />
                {trendTableNrDates > 1 && columnDates.map(date => <Table.HeaderCell key={date} className="unsortable" textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>)}
                {trendTableNrDates > 1 && <SortableTableHeaderCell column="unit" label="Unit" {...sortProps} />}
                {trendTableNrDates === 1 && !hiddenColumns.includes("trend") && <Table.HeaderCell className="unsortable" width="2">Trend (7 days)</Table.HeaderCell>}
                {trendTableNrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' {...sortProps} />}
                {trendTableNrDates === 1 && !hiddenColumns.includes("measurement") && <SortableTableHeaderCell column='measurement' label='Measurement' {...sortProps} />}
                {trendTableNrDates === 1 && !hiddenColumns.includes("target") && <SortableTableHeaderCell column='target' label='Target' {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableTableHeaderCell column='source' label='Source' {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableTableHeaderCell column='comment' label='Comment' {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableTableHeaderCell column='issues' label='Issues' {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableTableHeaderCell column='tags' label='Tags' {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}