/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

When('The admin approves the user', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserInfo(`${cypressUser.selector.id}`, `${csrfToken}`, Cypress.env('cypressName'), Cypress.env('cypressName'),
      Cypress.env('cypressStt'), Cypress.env('cypressGroup'), 'Approved')
    })
  })
})

Then('The user can see the hompage', () => {
  cy.visit('/home')
  cy.contains('You have been approved for access to TDP.').should('exist')
})

When('The user is in begin state', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.reinitUserAccount(`${cypressUser.selector.id}`, `${csrfToken}`)
    })
  })
})

When('The user requests access', () => {
  cy.get('#firstName').type(Cypress.env('cypressName'))
  cy.get('#lastName').type(Cypress.env('cypressName'))
  cy.get('#stt').type(Cypress.env('cypressSttName') + '{enter}')
  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(500).then(() => {
    cy.contains('Request Submitted').should('exist')
  })
})

When('The admin denies the user', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserInfo(`${cypressUser.selector.id}`, `${csrfToken}`, Cypress.env('cypressName'), Cypress.env('cypressName'),
      Cypress.env('cypressStt'), Cypress.env('cypressGroup'), 'Denied')
    })
  })
})

Then('The user sees request page again', () => {
  cy.visit('/home')
})

When('The admin deactivates the user account', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserInfo(`${cypressUser.selector.id}`, `${csrfToken}`, Cypress.env('cypressName'), Cypress.env('cypressName'),
      Cypress.env('cypressStt'), Cypress.env('cypressGroup'), 'Deactivated')
    })
  })
})

Then('The user cannot log in', () => {
  cy.visit('/')
  cy.contains('Inactive Account').should('exist')
})
Then('The user sees the request still submitted', () => {
  cy.visit('/')
  cy.contains('Request Submitted').should('exist')
})

When('The admin puts the user in pending', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.changeUserInfo(`${cypressUser.selector.id}`, `${csrfToken}`, Cypress.env('cypressName'), Cypress.env('cypressName'),
      Cypress.env('cypressStt'), Cypress.env('cypressGroup'), 'Pending')
    })
  })
})