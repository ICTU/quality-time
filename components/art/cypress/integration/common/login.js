import {Given} from "cypress-cucumber-preprocessor/steps";

Given(/^the quality manager logs in$/, () => {
    cy.visit("/");
    cy.get(".button").contains('Login').click();
    cy.fixture('credentials.json').then((credentials) =>
        cy.get('input[name="username"]')
            .type(credentials.username));
    cy.fixture('credentials.json').then((credentials) =>
        cy.get('input[name="password"]')
            .type(credentials.password));
    cy.get('.button').contains('Submit').click()
});
