import { Accordion, AccordionDetails, AccordionSummary } from "@mui/material"
import { accordionSummaryClasses } from "@mui/material/AccordionSummary"
import { string } from "prop-types"

import { childrenPropType, settingsPropType } from "../sharedPropTypes"
import { Header } from "./Header"
import { CaretRight } from "./icons"

export function HeaderWithDetails({ children, header, item_uuid, level, settings, subheader }) {
    const showDetails = Boolean(settings.expandedItems.includes(item_uuid))
    return (
        <Accordion
            disableGutters // Prevent the accordion summary from moving down when expanding the accordion
            elevation={0}
            expanded={showDetails}
            onChange={() => settings.expandedItems.toggle(item_uuid)}
            slotProps={{ transition: { unmountOnExit: true } }} // Make testing for (dis)appearance of contents easier
            slots={{ heading: "div" }}
            sx={{
                "&:before": {
                    display: "none", // Remove top border
                },
            }}
        >
            <AccordionSummary
                aria-controls={showDetails ? `accordion-content-${item_uuid}` : null}
                aria-label="Expand/collapse"
                expandIcon={<CaretRight size={{ h1: "48px", h2: "32px", h3: "24px" }[level]} />}
                id={`accordion-header-${item_uuid}`}
                sx={{
                    border: "0",
                    flexDirection: "row-reverse",
                    height: "80px",
                    padding: "0px",
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
    item_uuid: string,
    level: string,
    settings: settingsPropType,
    subheader: string,
}
