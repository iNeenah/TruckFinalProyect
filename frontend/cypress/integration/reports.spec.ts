describe('Reports Flow', () => {
  beforeEach(() => {
    // Iniciar sesión antes de cada test
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Verificar que se redirige al dashboard
    cy.url().should('include', '/');
  });

  it('debería navegar a la página de reportes', () => {
    // Navegar a la página de reportes
    cy.get('[data-testid="reports-link"]').click();
    cy.url().should('include', '/reports');
    
    // Verificar que se muestra la página de reportes
    cy.get('[data-testid="reports-page"]').should('be.visible');
    cy.get('[data-testid="statistics-section"]').should('be.visible');
    cy.get('[data-testid="saved-routes-section"]').should('be.visible');
  });

  it('debería generar un reporte correctamente', () => {
    // Navegar a la página de reportes
    cy.get('[data-testid="reports-link"]').click();
    
    // Hacer clic en generar reporte
    cy.get('[data-testid="generate-report-button"]').click();
    
    // Verificar que se muestra el reporte generado
    cy.get('[data-testid="report-content"]').should('be.visible');
  });

  it('debería exportar reporte a PDF', () => {
    // Navegar a la página de reportes
    cy.get('[data-testid="reports-link"]').click();
    
    // Hacer clic en exportar a PDF
    cy.get('[data-testid="export-pdf-button"]').click();
    
    // Verificar que se inicia la descarga (no se puede verificar completamente en Cypress)
    // Pero podemos verificar que no hay errores
    cy.on('window:alert', (str) => {
      expect(str).to.contain('Exportando');
    });
  });

  it('debería mostrar mensaje cuando no hay rutas guardadas', () => {
    // Simular que no hay rutas guardadas
    cy.window().then((win) => {
      win.localStorage.setItem('savedRoutes', JSON.stringify([]));
    });
    
    // Navegar a la página de reportes
    cy.get('[data-testid="reports-link"]').click();
    
    // Verificar que se muestra mensaje de no hay rutas
    cy.get('[data-testid="no-routes-message"]').should('be.visible');
  });
});