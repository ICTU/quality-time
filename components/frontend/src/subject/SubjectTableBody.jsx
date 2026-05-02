import { TableBody } from "@mui/material"
import { array, func, string } from "prop-types"
import React, { useEffect, useRef, useState } from "react"

function useSyncedEntries(metricEntries) {
    const [entries, setEntries] = useState(metricEntries)
    const prevEntriesRef = useRef(metricEntries)
    if (prevEntriesRef.current !== metricEntries) {
        prevEntriesRef.current = metricEntries
        setEntries(metricEntries)
    }
    return [entries, setEntries]
}

import { setMetricAttribute } from "../api/metric"
import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { createDragGhost } from "../utils"
import { SubjectTableRow } from "./SubjectTableRow"

export function SubjectTableBody({
    columnsToHide,
    dates,
    fieldsWithUrlAvailabilityErrors,
    handleSort,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    reversedMeasurements,
    settings,
    subjectUuid,
}) {
    const [entries, setEntries] = useSyncedEntries(metricEntries)
    const [dragOverIndex, setDragOverIndex] = useState(null)

    const dragItemRef = useRef(null)
    const dragOverItemRef = useRef(null)

    const handleDragStart = (index, rowRef, event) => {
        dragItemRef.current = index
        event.dataTransfer.effectAllowed = "move"
        createDragGhost(rowRef, event)
    }

    const handleDragEnter = (index) => {
        setDragOverIndex(index)
        dragOverItemRef.current = index
    }

    const handleDrop = (e) => {
        e.preventDefault()
        const dragFrom = dragItemRef.current
        const dropTarget = dragOverItemRef.current

        if (dragFrom == null || dropTarget == null || dragFrom === dropTarget) return

        const updatedEntries = [...entries]
        const [movedEntry] = updatedEntries.splice(dragFrom, 1)
        updatedEntries.splice(dropTarget, 0, movedEntry)

        // Optimistically update local UI
        setEntries(updatedEntries)

        dragItemRef.current = null
        dragOverItemRef.current = null
        setDragOverIndex(null)

        const [movedUUID] = movedEntry

        setMetricAttribute(movedUUID, "position_index", dropTarget, reload).catch((error) => {
            console.error("Failed to update metric position:", error)
            reload()
        })
    }

    useEffect(() => {
        const handleDragEnd = () => {
            dragItemRef.current = null
            dragOverItemRef.current = null
            setDragOverIndex(null)
        }

        globalThis.addEventListener("dragend", handleDragEnd)
        return () => {
            globalThis.removeEventListener("dragend", handleDragEnd)
        }
    }, [])

    const lastIndex = entries.length - 1

    return (
        <TableBody>
            {entries.map(([metricUuid, metric], index) => (
                <React.Fragment key={metricUuid}>
                    {dragOverIndex === index && (
                        <tr style={{ height: "4px" }}>
                            <td colSpan="100%">
                                <div
                                    data-testid={`drop-indicator-${index}`}
                                    style={{
                                        height: "4px",
                                        backgroundColor: "#1976d2",
                                        boxShadow: "0 0 3px rgba(25, 118, 210, 0.8)",
                                        borderRadius: "2px",
                                        margin: "2px 0",
                                    }}
                                />
                            </td>
                        </tr>
                    )}
                    <SubjectTableRow
                        columnsToHide={columnsToHide}
                        dates={dates}
                        fieldsWithUrlAvailabilityErrors={fieldsWithUrlAvailabilityErrors}
                        handleSort={handleSort}
                        index={index}
                        key={metricUuid}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metricUuid={metricUuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subjectUuid={subjectUuid}
                        onDragStart={handleDragStart}
                        onDragEnter={handleDragEnter}
                        onDrop={(e) => handleDrop(e)}
                    />
                </React.Fragment>
            ))}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    columnsToHide: stringsPropType,
    dates: datesPropType,
    fieldsWithUrlAvailabilityErrors: stringsPropType,
    handleSort: func,
    measurements: measurementsPropType,
    metricEntries: array,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: measurementsPropType,
    settings: settingsPropType,
    subjectUuid: string,
}
