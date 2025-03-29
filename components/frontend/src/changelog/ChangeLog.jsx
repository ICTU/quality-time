import UpdateIcon from "@mui/icons-material/Update"
import { Button, List, ListItem, ListItemAvatar, ListItemText, Stack, Typography } from "@mui/material"
import { string } from "prop-types"
import React, { useEffect, useState } from "react"

import { getChangelog } from "../api/changelog"
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

function ChangeLogWithoutMemo({ reportUuid, subjectUuid, metricUuid, sourceUuid, timestamp }) {
    const [changes, setChanges] = useState([])
    const [nrChanges, setNrChanges] = useState(5)
    useEffect(() => {
        let didCancel = false
        let uuids = {}
        if (reportUuid) {
            uuids.report_uuid = reportUuid
        }
        if (subjectUuid) {
            uuids.subject_uuid = subjectUuid
        }
        if (metricUuid) {
            uuids.metric_uuid = metricUuid
        }
        if (sourceUuid) {
            uuids.source_uuid = sourceUuid
        }
        getChangelog(nrChanges, uuids)
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
    }, [reportUuid, subjectUuid, metricUuid, sourceUuid, timestamp, nrChanges])

    let scope = "Changes in this instance of Quality-time"
    if (reportUuid) {
        scope = "Changes in this report"
    }
    if (subjectUuid) {
        scope = "Changes to this subject"
    }
    if (metricUuid) {
        scope = "Changes to this metric and its sources"
    }
    if (sourceUuid) {
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
    reportUuid: string,
    subjectUuid: string,
    metricUuid: string,
    sourceUuid: string,
    timestamp: string,
}

// Use React.memo so the ChangeLog is not re-rendered on reload, but only when one of its props change
export const ChangeLog = React.memo(function ChangeLog(props) {
    return <ChangeLogWithoutMemo {...props} />
})
