import "./Card.css"

import { useContext } from "react"
import { Card as SemanticUICard } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { addInvertedClassNameWhenInDarkMode } from "./dark_mode"

export function Card(props) {
    return <SemanticUICard {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
}

Card.Content = SemanticUICard.Content
Card.Description = SemanticUICard.Description
Card.Group = SemanticUICard.Group
Card.Header = SemanticUICard.Header
Card.Meta = SemanticUICard.Meta
