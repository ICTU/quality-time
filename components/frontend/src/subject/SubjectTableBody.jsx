import { TableBody } from "@mui/material"
import { array, func, string } from "prop-types"
import React, { useEffect, useRef, useState } from "react"

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
    changedFields,
    columnsToHide,
    dates,
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
    const [entries, setEntries] = useState(metricEntries)
    const [dragOverIndex, setDragOverIndex] = useState(null)

    const dragItem = useRef(null)
    const dragOverItem = useRef(null)
    const tableIdRef = useRef(subjectUuid)

    useEffect(() => {
        // Keep local entries in sync when external entries change
        setEntries(metricEntries)
    }, [metricEntries])

    const handleDragStart = (index, rowRef, event) => {
        dragItem.current = index
        event.dataTransfer.effectAllowed = "move"
        event.dataTransfer.setData("application/x-table-id", tableIdRef.current)
        createDragGhost(rowRef, event)
        // Set a global variable to track the active drag table
        window.__activeDragTableId = tableIdRef.current
    }

    const handleDragEnter = (index, event) => {
        // Use a global variable as fallback for test env and browsers that don't propagate dataTransfer
        const dragTableId = event?.dataTransfer?.getData("application/x-table-id") || window.__activeDragTableId
        if (dragTableId !== tableIdRef.current) return
        setDragOverIndex(index)
        dragOverItem.current = index
    }

    const handleDrop = (e) => {
        e.preventDefault()
        const dragTableId = e.dataTransfer?.getData("application/x-table-id") || window.__activeDragTableId
        if (dragTableId !== tableIdRef.current) return
        const dragFrom = dragItem.current
        const dropTarget = dragOverItem.current

        if (dragFrom == null || dropTarget == null || dragFrom === dropTarget) return

        const updatedEntries = [...entries]
        const [movedEntry] = updatedEntries.splice(dragFrom, 1)
        updatedEntries.splice(dropTarget, 0, movedEntry)

        // Optimistically update local UI
        setEntries(updatedEntries)

        dragItem.current = null
        dragOverItem.current = null
        setDragOverIndex(null)
        window.__activeDragTableId = undefined

        const [movedUUID] = movedEntry

        setMetricAttribute(movedUUID, "position_index", dropTarget, reload).catch((error) => {
            console.error("Failed to update metric position:", error)
            reload()
        })
    }

    useEffect(() => {
        const handleDragEnd = () => {
            dragItem.current = null
            dragOverItem.current = null
            setDragOverIndex(null)
            window.__activeDragTableId = undefined
        }

        window.addEventListener("dragend", handleDragEnd)
        return () => {
            window.removeEventListener("dragend", handleDragEnd)
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
                        changedFields={changedFields}
                        dates={dates}
                        columnsToHide={columnsToHide}
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
                        onDragEnter={(e) => handleDragEnter(index, e)}
                        onDrop={(e) => handleDrop(e)}
                        isDropTarget={dragOverIndex === index}
                    />
                </React.Fragment>
            ))}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    changedFields: stringsPropType,
    columnsToHide: stringsPropType,
    dates: datesPropType,
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
