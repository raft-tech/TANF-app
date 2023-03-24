import { When } from '@badeball/cypress-cucumber-preprocessor'

When('I visit the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})
