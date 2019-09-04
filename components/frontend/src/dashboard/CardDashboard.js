import React, { useState } from 'react';
import { Segment } from 'semantic-ui-react';
import RGL, { WidthProvider } from "react-grid-layout";

const ReactGridLayout = WidthProvider(RGL);

export function CardDashboard({ uuid, cards }) {
    const [dragging, setDragging] = useState(false);
    const [mousePos, setMousePos] = useState([0, 0, 0]);
    const [layout, setLayout] = useState(JSON.parse(localStorage.getItem(`layout-${uuid}`) || '[]'));
    if (cards.length === 0) { return null }
    function onLayoutChange(new_layout) {
        setLayout(new_layout);
        localStorage.setItem(`layout-${uuid}`, JSON.stringify(new_layout))
    }
    function onDragStart(current_layout, oldItem, newItem, placeholder, event) {
        setDragging(true);
        const now = new Date();
        setMousePos([event.clientX, event.clientY, now.getTime()]);
    }
    function onDragStop(current_layout, oldItem, newItem, placeholder, event) {
        const now = new Date();
        const distanceX = Math.abs(event.clientX - mousePos[0]);
        const distanceY = Math.abs(event.clientY - mousePos[1]);
        const timedelta = now.getTime() - mousePos[2];
        if (distanceX > 10 || distanceY > 10 || timedelta > 250) {
            setTimeout(() => setDragging(false), 200);  // User was dragging, prevent click event propagation
        } else {
            setDragging(false);  // User was clicking, don't prevent click event propagation
        }
    }
    const cols = 32;
    const card_width = 4;
    const card_height = 6;
    let divs = [];
    cards.forEach(
        (card, index) => divs.push(
            <div
                onClickCapture={(e) => { if (dragging) { e.stopPropagation() } }}
                key={card.key}
                data-grid={
                    {
                        i: card.key,
                        x: (card_width * index) % cols,
                        y: card_height * Math.trunc((card_width * index) / cols),
                        w: card_width,
                        h: card_height,
                        isResizable: false
                    }
                }
            >
                {card}
            </div>)
    )
    return (
        <Segment>
            <ReactGridLayout
                cols={cols}
                compactType={null}
                layout={layout}
                onDragStart={onDragStart}
                onDragStop={onDragStop}
                onLayoutChange={onLayoutChange}
                preventCollision={true}
                rowHeight={24}
            >
                {divs}
            </ReactGridLayout>
        </Segment>
    )
}
