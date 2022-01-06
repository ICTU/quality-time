import { Dropdown, Table } from "semantic-ui-react";
import { HamburgerMenu } from "../widgets/HamburgerMenu";
import { pluralize } from "../utils";

export function TrendTableHeader({ extraHamburgerItems, columnDates, hiddenColumns, trendTableNrDates, setTrendTableNrDates, trendTableInterval, setTrendTableInterval }) {
    return (
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell textAlign="center">
                    <HamburgerMenu>
                        {extraHamburgerItems}
                        <Dropdown.Item key="nr_dates">
                            <Dropdown text="Number of dates">
                                <Dropdown.Menu>
                                    {[2, 3, 4, 5, 6, 7].map((nr) =>
                                        <Dropdown.Item key={nr} active={nr === trendTableNrDates} onClick={() => setTrendTableNrDates(nr)}>{nr}</Dropdown.Item>
                                    )}
                                </Dropdown.Menu>
                            </Dropdown>
                        </Dropdown.Item>
                        <Dropdown.Item key="time_between_dates">
                            <Dropdown text="Time between dates">
                                <Dropdown.Menu>
                                    <Dropdown.Item key={1} active={1 === trendTableInterval} onClick={() => setTrendTableInterval(1)}>1 day</Dropdown.Item>
                                    {[7, 14, 21, 28].map((nr) =>
                                        <Dropdown.Item key={nr} active={nr === trendTableInterval} onClick={() => setTrendTableInterval(nr)}>{`${nr/7} ${pluralize("week", nr/7)}`}</Dropdown.Item>
                                    )}
                                </Dropdown.Menu>
                            </Dropdown>
                        </Dropdown.Item>
                    </HamburgerMenu>
                </Table.HeaderCell>
                <Table.HeaderCell>Metric</Table.HeaderCell>
                {columnDates.map(date => <Table.HeaderCell key={date} textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>)}
                <Table.HeaderCell>Unit</Table.HeaderCell>
                {!hiddenColumns.includes("issues") && <Table.HeaderCell>Issues</Table.HeaderCell>}
            </Table.Row>
        </Table.Header>
    )
}