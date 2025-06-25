import { Accordion, AccordionDetails, AccordionSummary } from "@mui/material"
import { accordionSummaryClasses } from "@mui/material/AccordionSummary"
import { string } from "prop-types"

import { childrenPropType, settingsPropType } from "../sharedPropTypes"
import { Header } from "./Header"
import { CaretRight } from "./icons"

export function HeaderWithDetails({ children, header, itemUuid, level, settings, subheader }) {
    const showDetails = Boolean(settings.expandedItems.includes(itemUuid))
    return (
        <Accordion
            disableGutters // Prevent the accordion summary from moving down when expanding the accordion
            elevation={0}
            expanded={showDetails}
            onChange={() => settings.expandedItems.toggle(itemUuid)}
            slotProps={{ transition: { unmountOnExit: true } }} // Make testing for (dis)appearance of contents easier
            slots={{ heading: "div" }}
            sx={{
                "&:before": {
                    display: "none", // Remove top border
                },
            }}
        >
            <AccordionSummary
                aria-controls={showDetails ? `accordion-content-${itemUuid}` : null}
                aria-label="Expand/collapse"
                expandIcon={<CaretRight size={{ h1: "4rem", h2: "3rem", h3: "2rem" }[level]} />}
                id={`accordion-header-${itemUuid}`}
                sx={{
                    border: "0",
                    flexDirection: "row-reverse",
                    height: "80px",
                    padding: "0px",
                    paddingLeft: "0.5rem",
                    [`& .${accordionSummaryClasses.expandIconWrapper}.${accordionSummaryClasses.expanded}`]: {
                        transform: "rotate(90deg)",
                    },
                    color: "primary.main",
                }}
            >
                <Header header={header} level={level} subheader={subheader} />
            </AccordionSummary>
            <AccordionDetails sx={{ paddingLeft: "8px", paddingRight: "8px", paddingBottom: "0px" }}>
                {children}
            </AccordionDetails>
        </Accordion>
    )
}
HeaderWithDetails.propTypes = {
    children: childrenPropType,
    header: string,
    itemUuid: string,
    level: string,
    settings: settingsPropType,
    subheader: string,
}
