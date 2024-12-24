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
            sx={{
                "&:before": {
                    display: "none", // Remove top border
                },
            }}
        >
            <AccordionSummary
                aria-controls={`accordion-content-${item_uuid}`}
                expandIcon={<CaretRight />}
                id={`accordion-header-${item_uuid}`}
                sx={{
                    border: "0",
                    flexDirection: "row-reverse",
                    height: "60px",
                    padding: "0px",
                    [`& .${accordionSummaryClasses.expandIconWrapper}.${accordionSummaryClasses.expanded}`]: {
                        transform: "rotate(90deg)",
                    },
                    color: "primary.main",
                }}
            >
                <Header header={header} level={level} subheader={subheader} />
            </AccordionSummary>
            <AccordionDetails>{children}</AccordionDetails>
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
