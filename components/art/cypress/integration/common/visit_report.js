import {Given} from "cypress-cucumber-preprocessor/steps";

const url = "/example-report";

Given(/^the quality manager visits the report$/, () => {
    cy.visit(url);
    cy.title().should('eq', 'Quality-time');
});
