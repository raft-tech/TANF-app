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

Cypress.Commands.add('djangoAdminLogin', (username) => {
  cy
    .request({
      method: 'POST',
      url: 'http://localhost:8080/admin',
    })
})

// Update with correct info when we can get the token
Cypress.Commands.add('adminApproveUser', (username) => {
  cy
    .request({
      method: 'POST',
      url: `http://localhost:8080/admin/users/user/1ec4e20b-4e79-46eb-af1e-d640be91f1a3/change/`,
      body: {
        username: username,
        account_approval_status: 'Approved',
        _save: 'Save'
      }
    })
});

// Use this to get the tokens
Cypress.Commands.add('loginAdmin', (username, password) => {

  return cy.request({
    url: `${Cypress.env('apiUrl')}/login/cypress`,
    method: 'HEAD' // cookies are in the HTTP headers, so HEAD suffices
  }).then(() => {
    cy.getCookie('sessionid').should('not.exist')
    cy.getCookie('csrfmiddlewaretoken').its('value').then((token) => {
      let oldToken = token
      cy.request({
        url: `${Cypress.env('apiUrl')}/login/cypress`,
        method: 'POST',
        form: true,
        followRedirect: false, // no need to retrieve the page after login
        body: {
          username: username,
          password: password,
          csrfmiddlewaretoken: token
        }
      }).then(() => {

        cy.getCookie('sessionid').should('exist')
        return cy.getCookie('csrftoken').its('value')

      })
    })
  })

})