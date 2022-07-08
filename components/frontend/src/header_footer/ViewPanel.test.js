import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ViewPanel } from './ViewPanel';

let settingsFixture = {
    date_interval: 7,
    date_order: "descending",
    hidden_columns: [],
    hide_metrics_not_requiring_action: false,
    nr_dates: 1,
    sort_column: null,
    sort_direction: "ascending",
    tabs: [],
    show_issue_summary: false,
    show_issue_creation_date: false,
    show_issue_update_date: false,
    ui_mode: null
}

it("clears the visible details tabs", async () => {
    const  postSettings = jest.fn();
    const settings = {...settingsFixture, tabs: ["tab"]}
    await act(async () => {
        render(<ViewPanel postSettings={postSettings} settings={settings} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(postSettings).toHaveBeenCalled()
})

it("doesn't clear the visible details tabs if there are none", async () => {
    const postSettings = jest.fn();
    const settings = {...settingsFixture, tabs: []}
    await act(async () => {
        render(<ViewPanel postSettings={postSettings} settings={settings} />)
        fireEvent.click(screen.getByText(/Collapse all metrics/))
    });
    expect(postSettings).not.toHaveBeenCalled()
})

function eventHandlers() {
    return {
        setSettings: jest.fn(),
        handleSort: jest.fn(),
    }
}

it('resets the settings', async () => {
    const props = eventHandlers();
    const settings = {...settingsFixture, sort_column: "source"}
    await act(async () => {
        render(
            <ViewPanel
                settings={settings}
                userSettings={settingsFixture}
                {...props}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(props.setSettings).toHaveBeenCalled()
    expect(props.handleSort).toHaveBeenCalled()
})

it('does not reset the settings when all have the default value', async () => {
    const props = eventHandlers();
    await act(async () => {
        render(
            <ViewPanel
                settings={settingsFixture}
                userSettings={settingsFixture}
                {...props}
            />
        )
        fireEvent.click(screen.getByText(/Reset all settings/))
    });
    expect(props.setSettings).not.toHaveBeenCalled()
    expect(props.handleSort).not.toHaveBeenCalled()
})

it("sets dark mode", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/Dark mode/))
    });
    expect(setSettings).toHaveBeenCalledWith({ui_mode: "dark"})
})

it("sets light mode", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/Light mode/))
    });
    expect(setSettings).toHaveBeenCalledWith({ui_mode: "light"})
})

it("sets dark mode on keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/Dark mode/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({ui_mode: "dark"})
})

it("hides the metrics not requiring action", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/Metrics requiring action/))
    });
    expect(setSettings).toHaveBeenCalledWith({"hide_metrics_not_requiring_action": true})
})

it("shows the metrics not requiring action", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/All metrics/))
    });
    expect(setSettings).toHaveBeenCalledWith({"hide_metrics_not_requiring_action": false})
})

it("shows the metrics not requiring action by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/All metrics/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"hide_metrics_not_requiring_action": false})
})

it("hides a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} settings={settingsFixture}  />)
        fireEvent.click(screen.getByText(/Trend/))
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("trend")
})

it("hides a column by keypress", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} settings={settingsFixture}  />)
        await userEvent.type(screen.getAllByText(/Comment/)[0], "{Enter}")
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("comment")
})

it("shows a column", async () => {
    const toggleHiddenColumn = jest.fn();
    await act(async () => {
        render(<ViewPanel toggleHiddenColumn={toggleHiddenColumn} settings={settingsFixture}  />)
        fireEvent.click(screen.getAllByText(/Status/)[0])
    });
    expect(toggleHiddenColumn).toHaveBeenCalledWith("status")
})

it("sorts a column", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel handleSort={handleSort} settings={settingsFixture}  />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column descending", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel sortColumn="comment" sortDirection="ascending" handleSort={handleSort} settings={settingsFixture}  />)
        fireEvent.click(screen.getAllByText(/Comment/)[1])
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn();
    await act(async () => {
        render(<ViewPanel handleSort={handleSort} settings={settingsFixture} />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    const setSettings = jest.fn();
    const settings = {...settingsFixture, hidden_columns: ["comment"]}
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settings} />)
        await userEvent.type(screen.getAllByText(/Comment/)[1], "{Enter}")
    });
    expect(setSettings).not.toHaveBeenCalledWith()
})

it("sets the number of dates", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/7 dates/))
    });
    expect(setSettings).toHaveBeenCalledWith({"nr_dates": 7})
})

it("sets the number of dates by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/5 dates/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"nr_dates": 5})
})

it("sets the date interval to weeks", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/2 weeks/))
    });
    expect(setSettings).toHaveBeenCalledWith({"date_interval": 14})
})

it("sets the date interval to one day", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel  setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getByText(/1 day/))
    });
    expect(setSettings).toHaveBeenCalledWith({"date_interval": 1})
})

it("sets the date interval by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel  setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/1 day/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"date_interval": 1})
})

it("sorts the dates descending", async () => {
    const setSettings = jest.fn();
    const settings = {...settingsFixture, date_order: "ascending"}
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settings} />)
        fireEvent.click(screen.getByText(/Descending/))
    });
    expect(setSettings).toHaveBeenCalledWith({"date_order": "descending"})
})

it("sorts the dates ascending by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getByText(/Ascending/), "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"date_order": "ascending"})
})

it("shows issue summaries", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        fireEvent.click(screen.getAllByText(/Summary/)[0])
    });
    expect(setSettings).toHaveBeenCalledWith({"show_issue_summary": true})
})

it("shows issue summaries by keypress", async () => {
    const setSettings = jest.fn();
    await act(async () => {
        render(<ViewPanel setSettings={setSettings} settings={settingsFixture} />)
        await userEvent.type(screen.getAllByText(/Summary/)[0], "{Enter}")
    });
    expect(setSettings).toHaveBeenCalledWith({"show_issue_summary": true})
})
