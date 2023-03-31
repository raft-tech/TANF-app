import { When } from '@badeball/cypress-cucumber-preprocessor'

When('The user visits the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('The new user logs in', () => {
  cy.login('new-cypress@teamraft.com')
})

When('The admin logs in', () => {
  cy.adminLogin('cypress-admin@teamraft.com')
})

When('The user logs in', () => {
  cy.login('new-cypress@teamraft.com')
})