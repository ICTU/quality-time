import React, { useState } from 'react';
import RGL, { WidthProvider } from "react-grid-layout";
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

const ReactGridLayout = WidthProvider(RGL);

function cardDivs(cards, isDragging) {
    return cards.map((card) => (
        <div
            onClickCapture={(e) => { if (isDragging(e)) { e.stopPropagation() } }}
            key={card.key}
        >
            {card}
        </div>
    ));
}

function defaultLayout(cards, cols, cardWidth = 4, cardHeight = 6) {
    return cards.map((card, index) => (
        {
            i: card.key,
            x: (cardWidth * index) % cols,
            y: cardHeight * Math.trunc((cardWidth * index) / cols),
            w: cardWidth,
            h: cardHeight,
            isResizable: false
        }
    ))
}

export function CardDashboard({ cards, initialLayout, saveLayout }) {
    const cols = 32;
    const [dragging, setDragging] = useState(false);
    const [mousePos, setMousePos] = useState([0, 0, 0]);
    if (cards.length === 0) { return null }
    const layout = initialLayout?.length === 0 ? defaultLayout(cards, cols) : initialLayout
    function onDragStart(_currentLayout, _oldItem, _newItem, _placeholder, event) {
        setDragging(true);
        const now = new Date();
        setMousePos([event.clientX, event.clientY, now.getTime()]);
    }
    function onDragStop(newLayout, _oldItem, _newItem, _placeholder, _event) {
        saveLayout(newLayout)
        setTimeout(() => setDragging(false), 200);  // User was dragging, prevent click event propagation
    }
    function isDragging(event) {
        const now = new Date();
        const distanceX = Math.abs(event.clientX - mousePos[0]);
        const distanceY = Math.abs(event.clientY - mousePos[1]);
        const timedelta = now.getTime() - mousePos[2];
        return (distanceX > 10 || distanceY > 10 || timedelta > 250) ? dragging : false;
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
            >
                {cardDivs(cards, isDragging)}
            </ReactGridLayout>)}
        </Permissions.Consumer>
    )
}
