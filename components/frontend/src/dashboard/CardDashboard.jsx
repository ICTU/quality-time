import { array, arrayOf, bool, element, func } from "prop-types"
import { useEffect, useState } from "react"
import ReactGridLayout, { noCompactor, useContainerWidth } from "react-grid-layout"

import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"

function cardDivs(cards, isDragging) {
    return cards.map((card) => (
        <div
            onClickCapture={(e) => {
                if (isDragging(e)) {
                    e.stopPropagation()
                }
            }}
            key={card.key}
        >
            {card}
        </div>
    ))
}
cardDivs.propTypes = {
    cards: arrayOf(element),
    dragging: bool,
    isDragging: func,
}

export function CardDashboard({ cards, initialLayout, saveLayout }) {
    const cols = 32
    const cardWidth = 4
    const cardHeight = 6
    const { width, containerRef, mounted } = useContainerWidth()
    const [mousePos, setMousePos] = useState([0, 0, 0])
    const [dragging, setDragging] = useState(false)
    useEffect(() => {
        const dashboard = document.getElementById("dashboard")
        Promise.all(dashboard.getAnimations().map((animation) => animation.finished))
            .then(() => dashboard.classList.add("animated")) // The animated class is used by the renderer to wait for animations to finish
            .catch((error) => console.log(error)) // No toast message: chances this goes wrong are small and a toaster could end up in the PDF
    }, [])
    if (cards.length === 0) {
        return null
    }
    const cardKeys = cards.map((card) => card.key)
    const layout = (initialLayout ?? []).filter((layoutItem) => cardKeys.includes(layoutItem.i))
    const layoutItemIds = layout.map((layoutItem) => layoutItem.i)
    const newCards = cards.filter((card) => !layoutItemIds.includes(card.key))
    const maxY = layout.length === 0 ? 0 : Math.max(...layout.map((card) => card.y)) + cardHeight
    newCards.forEach((card, index) =>
        layout.push({
            i: card.key,
            x: (index * cardWidth) % cols,
            y: maxY + cardHeight * Math.trunc((cardWidth * index) / cols),
            w: cardWidth,
            h: cardHeight,
            isResizable: false,
        }),
    )

    function onDragStart(_currentLayout, _oldItem, _newItem, _placeholder, event) {
        setDragging(true)
        const now = new Date()
        setMousePos([event.clientX, event.clientY, now.getTime()])
    }

    function onDragStop(newLayout, _oldItem, _newItem, _placeholder, event) {
        if (isDragging(event) && newLayout !== layout) {
            saveLayout(newLayout)
        }
        setTimeout(() => setDragging(false), 200) // User was dragging, prevent click event propagation
    }

    function isDragging(event) {
        if (dragging) {
            const now = new Date()
            const distanceX = Math.abs(event.clientX - mousePos[0])
            const distanceY = Math.abs(event.clientY - mousePos[1])
            const timedelta = now.getTime() - mousePos[2]
            return distanceX > 10 || distanceY > 10 || timedelta > 250
        }
        return false
    }

    return (
        <Permissions.Consumer>
            {(permissions) => (
                <div ref={containerRef}>
                    {mounted && (
                        <ReactGridLayout
                            compactor={noCompactor}
                            isDraggable={accessGranted(permissions, [EDIT_REPORT_PERMISSION])}
                            gridConfig={{ cols: cols, rowHeight: 24 }}
                            layout={layout}
                            measureBeforeMount={true}
                            onDragStart={onDragStart}
                            onDragStop={onDragStop}
                            preventCollision={true}
                            useCSSTransforms={false} // Don't fly-in the cards from the top left
                            width={width}
                        >
                            {cardDivs(cards, isDragging)}
                        </ReactGridLayout>
                    )}
                </div>
            )}
        </Permissions.Consumer>
    )
}
CardDashboard.propTypes = {
    cards: arrayOf(element),
    initialLayout: array,
    saveLayout: func,
}
