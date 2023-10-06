import React, { useEffect, useState } from 'react';
import RGL, { WidthProvider } from "react-grid-layout";
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

const ReactGridLayout = WidthProvider(RGL);

function cardDivs(cards, dragging, isDragging) {
    return cards.map((card) => (
        <div
            onClickCapture={(e) => { if (isDragging(e)) { e.stopPropagation() } }}
            key={card.key}
            style={{ transition: dragging ? "0ms" : "400ms" }}
        >
            {card}
        </div>
    ));
}

export function CardDashboard({ cards, initialLayout, saveLayout }) {
    const cols = 32;
    const cardWidth = 4
    const cardHeight = 6
    const [mousePos, setMousePos] = useState([0, 0, 0]);
    const [dragging, setDragging] = useState(false);
    useEffect(() => {
        const dashboard = document.getElementById("dashboard");
        Promise.all(
            dashboard.getAnimations().map(animation => animation.finished)
        ).then(
            () => dashboard.classList.add("animated")  // Used by the renderer to wait for animations to finish
        )
    }, []);
    if (cards.length === 0) { return null }
    const cardKeys = cards.map((card) => card.key)
    const layout = (initialLayout ?? []).filter((layoutItem) => cardKeys.includes(layoutItem.i))
    const layoutItemIds = layout.map((layoutItem) => layoutItem.i)
    const newCards = cards.filter((card) => !layoutItemIds.includes(card.key))
    const maxY = layout.length === 0 ? 0 : Math.max(...layout.map((card) => card.y)) + cardHeight
    newCards.forEach((card, index) => layout.push(
        {
            i: card.key,
            x: (index * cardWidth) % cols,
            y: maxY + cardHeight * Math.trunc((cardWidth * index) / cols),
            w: cardWidth,
            h: cardHeight,
            isResizable: false
        }
    ))

    function onDragStart(_currentLayout, _oldItem, _newItem, _placeholder, event) {
        setDragging(true);
        const now = new Date();
        setMousePos([event.clientX, event.clientY, now.getTime()]);
    }

    function onDragStop(newLayout, _oldItem, _newItem, _placeholder, _event) {
        if (newLayout !== layout) {
            saveLayout(newLayout)
        }
        setTimeout(() => setDragging(false), 200);  // User was dragging, prevent click event propagation
    }

    function isDragging(event) {
        if (dragging) {
            const now = new Date();
            const distanceX = Math.abs(event.clientX - mousePos[0]);
            const distanceY = Math.abs(event.clientY - mousePos[1]);
            const timedelta = now.getTime() - mousePos[2];
            return distanceX > 10 || distanceY > 10 || timedelta > 250
        }
        return false
    }

    return (
        <Permissions.Consumer>{(permissions) => (
            <ReactGridLayout
                cols={cols}
                compactType={null}
                isDraggable={accessGranted(permissions, [EDIT_REPORT_PERMISSION])}
                layout={layout}
                onDragStart={onDragStart}
                onDragStop={onDragStop}
                preventCollision={true}
                rowHeight={24}
                style={{
                    zIndex: "0",  // Prevent cards from being shown above the settings panel after being clicked
                }}
            >
                {cardDivs(cards, dragging, isDragging)}
            </ReactGridLayout>)}
        </Permissions.Consumer>
    )
}