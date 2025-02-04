import UpdateIcon from "@mui/icons-material/Update"
import { Button, List, ListItem, ListItemAvatar, ListItemText, Stack, Typography } from "@mui/material"
import { string } from "prop-types"
import React, { useEffect, useState } from "react"

import { get_changelog } from "../api/changelog"
import { Avatar } from "../widgets/Avatar"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { showMessage } from "../widgets/toast"

function Event({ description, email, timestamp }) {
    return (
        <ListItem sx={{ padding: "0px" }}>
            <ListItemAvatar>
                <Avatar email={email} />
            </ListItemAvatar>
            <ListItemText primary={description} secondary={<TimeAgoWithDate date={timestamp} />} />
        </ListItem>
    )
}
Event.propTypes = {
    description: string,
    email: string,
    timestamp: string,
}

function ChangeLogWithoutMemo({ report_uuid, subject_uuid, metric_uuid, source_uuid, timestamp }) {
    const [changes, setChanges] = useState([])
    const [nrChanges, setNrChanges] = useState(5)
    useEffect(() => {
        let didCancel = false
        let uuids = {}
        if (report_uuid) {
            uuids.report_uuid = report_uuid
        }
        if (subject_uuid) {
            uuids.subject_uuid = subject_uuid
        }
        if (metric_uuid) {
            uuids.metric_uuid = metric_uuid
        }
        if (source_uuid) {
            uuids.source_uuid = source_uuid
        }
        get_changelog(nrChanges, uuids)
            .then(function (json) {
                if (!didCancel) {
                    setChanges(json.changelog || [])
                }
                return null
            })
            .catch((error) => showMessage("error", "Could not fetch changes", `${error}`))
        return () => {
            didCancel = true
        }
    }, [report_uuid, subject_uuid, metric_uuid, source_uuid, timestamp, nrChanges])

    let scope = "Changes in this instance of Quality-time"
    if (report_uuid) {
        scope = "Changes in this report"
    }
    if (subject_uuid) {
        scope = "Changes to this subject"
    }
    if (metric_uuid) {
        scope = "Changes to this metric and its sources"
    }
    if (source_uuid) {
        scope = "Changes to this source"
    }

    return (
        <>
            <Stack direction="column">
                <Typography>{scope}</Typography>
                <Typography component="span" sx={{ fontSize: "80%" }}>
                    Most recent first
                </Typography>
            </Stack>
            <List dense>
                {changes.map((change) => (
                    <Event
                        key={change.timestamp + change.delta}
                        description={change.delta}
                        email={change.email}
                        timestamp={change.timestamp}
                    />
                ))}
            </List>
            <Button variant="outlined" onClick={() => setNrChanges(nrChanges + 10)} startIcon={<UpdateIcon />}>
                Load more changes
            </Button>
        </>
    )
}
ChangeLogWithoutMemo.propTypes = {
    report_uuid: string,
    subject_uuid: string,
    metric_uuid: string,
    source_uuid: string,
    timestamp: string,
}

// Use React.memo so the ChangeLog is not re-rendered on reload, but only when one of its props change
export const ChangeLog = React.memo(function ChangeLog(props) {
    return <ChangeLogWithoutMemo {...props} />
})
