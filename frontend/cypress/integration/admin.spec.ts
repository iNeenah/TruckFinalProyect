describe('Admin Panel Flow', () => {
  beforeEach(() => {
    // Iniciar sesión como administrador antes de cada test
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type('admin@example.com');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    
    // Verificar que se redirige al dashboard
    cy.url().should('include', '/');
  });

  it('debería navegar al panel de administración', () => {
    // Navegar al panel de administración
    cy.get('[data-testid="admin-link"]').click();
    cy.url().should('include', '/admin');
    
    // Verificar que se muestra el panel de administración
    cy.get('[data-testid="admin-panel"]').should('be.visible');
    cy.get('[data-testid="tolls-management"]').should('be.visible');
    cy.get('[data-testid="fuel-prices-management"]').should('be.visible');
    cy.get('[data-testid="users-management"]').should('be.visible');
  });

  it('debería gestionar peajes correctamente', () => {
    // Navegar al panel de administración
    cy.get('[data-testid="admin-link"]').click();
    
    // Navegar a la gestión de peajes
    cy.get('[data-testid="tolls-link"]').click();
    cy.url().should('include', '/admin/tolls');
    
    // Verificar que se muestra la página de gestión de peajes
    cy.get('[data-testid="tolls-page"]').should('be.visible');
  });

  it('debería gestionar precios de combustible correctamente', () => {
    // Navegar al panel de administración
    cy.get('[data-testid="admin-link"]').click();
    
    // Navegar a la gestión de precios de combustible
    cy.get('[data-testid="fuel-prices-link"]').click();
    cy.url().should('include', '/admin/fuel-prices');
    
    // Verificar que se muestra la página de gestión de precios
    cy.get('[data-testid="fuel-prices-page"]').should('be.visible');
  });

  it('debería gestionar usuarios correctamente', () => {
    // Navegar al panel de administración
    cy.get('[data-testid="admin-link"]').click();
    
    // Navegar a la gestión de usuarios
    cy.get('[data-testid="users-link"]').click();
    cy.url().should('include', '/admin/users');
    
    // Verificar que se muestra la página de gestión de usuarios
    cy.get('[data-testid="users-page"]').should('be.visible');
  });

  it('debería mostrar estadísticas del sistema', () => {
    // Navegar al panel de administración
    cy.get('[data-testid="admin-link"]').click();
    
    // Verificar que se muestran las estadísticas
    cy.get('[data-testid="vehicles-stat"]').should('be.visible');
    cy.get('[data-testid="routes-stat"]').should('be.visible');
    cy.get('[data-testid="users-stat"]').should('be.visible');
    cy.get('[data-testid="companies-stat"]').should('be.visible');
  });
});