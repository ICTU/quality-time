import React, { useState } from 'react';
import { Segment } from 'semantic-ui-react';
import RGL, { WidthProvider } from "react-grid-layout";

const ReactGridLayout = WidthProvider(RGL);

export function CardDashboard(props) {
    function onLayoutChange(layout) {
        localStorage.setItem(`layout-${props.uuid}`, JSON.stringify(layout))
    }

    if (props.cards.length === 0) { return null }
    const [dragging, setDragging] = useState(false);
    const [mousePos, setMousePos] = useState([0, 0, 0]);
    const cols = 32;
    const card_width = 4;
    const card_height = 6;
    let divs = [];
    props.cards.forEach(
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
    const layout = JSON.parse(localStorage.getItem(`layout-${props.uuid}`) || '[]');
    return (
        <Segment>
            <ReactGridLayout
                onDragStart={(layout, oldItem, newItem, placeholder, e) => {
                    setDragging(true);
                    const now = new Date();
                    setMousePos([e.clientX, e.clientY, now.getTime()]);
                }}
                onDragStop={(layout, oldItem, newItem, placeholder, e) => {
                    const now = new Date();
                    const distanceX = Math.abs(e.clientX - mousePos[0]);
                    const distanceY = Math.abs(e.clientY - mousePos[1]);
                    const timedelta = now.getTime() - mousePos[2];
                    if (distanceX > 10 || distanceY > 10 || timedelta > 250) {
                        setTimeout(() => setDragging(false), 200);  // User was dragging, prevent click event propagation
                    } else {
                        setDragging(false);  // User was clicking, don't prevent click event propagation
                    }
                }}
                cols={cols} rowHeight={24} layout={layout} preventCollision={true} compactType={null} onLayoutChange={onLayoutChange}
            >
                {divs}
            </ReactGridLayout>
        </Segment>
    )
}
