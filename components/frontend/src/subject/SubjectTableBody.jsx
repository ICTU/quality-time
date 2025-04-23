import { TableBody } from "@mui/material"
import { array, func, string } from "prop-types"
import React, { useEffect, useRef, useState } from "react"

import { set_metric_attribute } from "../api/metric"
import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { SubjectTableRow } from "./SubjectTableRow"
import { createDragGhost } from "../utils"

export function SubjectTableBody({
    changed_fields,
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
    subject_uuid,
}) {
    const [dragOverIndex, setDragOverIndex] = useState(null)

    const dragItem = useRef(null)
    const dragOverItem = useRef(null)

    const handleDragStart = (index, rowRef, event) => {
        dragItem.current = index
        event.dataTransfer.effectAllowed = "move"

        createDragGhost(rowRef, event)
    }

    const handleDragEnter = (index) => {
        setDragOverIndex(index)
        dragOverItem.current = index
    }

    const handleDrop = (e) => {
        e.preventDefault()
        const dragFrom = dragItem.current
        const dropTarget = dragOverItem.current

        if (dragFrom == null || dropTarget == null || dragFrom === dropTarget) return

        const [movedUUID] = metricEntries[dragFrom]

        dragItem.current = null
        dragOverItem.current = null
        setDragOverIndex(null)

        // Persist to backend and reload
        set_metric_attribute(movedUUID, "position_index", dropTarget, reload)
    }

    useEffect(() => {
        const handleDragEnd = () => {
            dragItem.current = null
            dragOverItem.current = null
            setDragOverIndex(null)
        }

        window.addEventListener("dragend", handleDragEnd)
        return () => {
            window.removeEventListener("dragend", handleDragEnd)
        }
    }, [])

    const lastIndex = metricEntries.length - 1

    return (
        <TableBody>
            {metricEntries.map(([metric_uuid, metric], index) => (
                <React.Fragment key={metric_uuid}>
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
                        changed_fields={changed_fields}
                        dates={dates}
                        handleSort={handleSort}
                        index={index}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metric_uuid={metric_uuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subject_uuid={subject_uuid}
                        onDragStart={handleDragStart}
                        onDragEnter={handleDragEnter}
                        onDrop={(e) => handleDrop(e)}
                        isDropTarget={dragOverIndex === index}
                    />
                </React.Fragment>
            ))}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    changed_fields: stringsPropType,
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
    subject_uuid: string,
}
