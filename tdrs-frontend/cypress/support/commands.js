/* eslint-disable no-undef */

// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('login', (username) =>
  cy
    .request({
      method: 'POST',
      url: `${Cypress.env('apiUrl')}/login/cypress`,
      body: {
        username,
        token: Cypress.env('cypressToken'),
      },
    })
    .then((response) => {
      cy.window()
        .its('store')
        .invoke('dispatch', {
          type: 'SET_AUTH',
          payload: {
            user: {
              email: username,
            },
          },
        })
    })
)

Cypress.Commands.add('adminLogin', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/login/cypress`,
    body: {
      username: 'cypress-admin@teamraft.com',
      token: Cypress.env('cypressToken'),
    },
  }).then((response) => {
    cy.getCookie('sessionid').its('value').as('adminSessionId')
    cy.getCookie('csrftoken').its('value').as('adminCsrfToken')

    // handle response, list of user emails/ids for use in adminApiRequest
    cy.get(response.body.users[0]).as("cypressUser")

    cy.clearCookie('sessionid')
    cy.clearCookie('csrftoken')

  })
})

Cypress.Commands.add('adminApiRequest', (options = {}) => {
  cy.get('@adminSessionId').then((sessionId) =>
    cy.setCookie('sessionid', sessionId)
  )
  cy.get('@adminCsrfToken').then((csrfToken) =>
    cy.setCookie('csrftoken', csrfToken)
  )

  cy.request(options).then((response) => {
    cy.clearCookie('sessionid')
    cy.clearCookie('csrftoken')
  }) 
})

Cypress.Commands.add('approveUser', (user, token) => {
  let options = {
    method: 'POST',
    url: `http://localhost:8080/admin/users/user/${user}/change/`,
    headers: { 'X_CSRFTOKEN': token },
    form: true,
    body: {
      username: 'new-cypress@teamraft.com', // This `'${cypressUser.selector.username}'` should work but it does not. There are extra characters in the username encoding for some reason.
      first_name: 'cypress',
      last_name: 'cypress',
      email: 'new-cypress@teamraft.com',
      stt: '6',
      account_approval_status: 'Approved',
      _save: 'Save'
    },
  }
  cy.adminApiRequest(options)
})

Cypress.Commands.add('reinitUserAccount', (user, token) => {
  let options = {
    method: 'POST',
    url: `http://localhost:8080/admin/users/user/${user}/change/`,
    headers: { 'X_CSRFTOKEN': token },
    form: true,
    body: {
      username: 'new-cypress@teamraft.com', // This `'${cypressUser.selector.username}'` should work but it does not. There are extra characters in the username encoding for some reason.
      first_name: '',
      last_name: '',
      email: 'new-cypress@teamraft.com',
      stt: '',
      account_approval_status: 'Initial',
      _save: 'Save'
    },
  }
  cy.adminApiRequest(options)
})
