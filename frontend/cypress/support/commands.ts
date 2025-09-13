// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// eslint-disable-next-line @typescript-eslint/no-namespace
declare namespace Cypress {
  interface Chainable<Subject> {
    login(email: string, password: string): Chainable<void>
    logout(): Chainable<void>
    createVehicle(vehicleData: any): Chainable<any>
  }
}

Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login')
  cy.get('input[name="email"]').type(email)
  cy.get('input[name="password"]').type(password)
  cy.get('button[type="submit"]').click()
  cy.url().should('not.include', '/login')
})

Cypress.Commands.add('logout', () => {
  // Implementation depends on your app's logout mechanism
  cy.get('[data-testid="user-menu"]').click()
  cy.get('[data-testid="logout-button"]').click()
  cy.url().should('include', '/login')
})

Cypress.Commands.add('createVehicle', (vehicleData) => {
  cy.visit('/vehicles')
  cy.get('[data-testid="add-vehicle-button"]').click()
  cy.get('input[name="name"]').type(vehicleData.name)
  cy.get('input[name="license_plate"]').type(vehicleData.license_plate)
  cy.get('select[name="fuel_type"]').select(vehicleData.fuel_type)
  cy.get('input[name="fuel_consumption"]').type(vehicleData.fuel_consumption.toString())
  cy.get('button[type="submit"]').click()
})