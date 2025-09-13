describe('Route Calculation Flow', () => {
  beforeEach(() => {
    // Iniciar sesión antes de cada test
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Verificar que se redirige al dashboard
    cy.url().should('include', '/');
  });

  it('debería calcular rutas correctamente', () => {
    // Navegar a la página de cálculo de rutas
    cy.get('[data-testid="routes-link"]').click();
    cy.url().should('include', '/routes');
    
    // Llenar el formulario de cálculo de rutas
    cy.get('[data-testid="origin-input"]').type('Buenos Aires');
    cy.get('[data-testid="destination-input"]').type('Rosario');
    cy.get('[data-testid="vehicle-select"]').select('ABC123');
    
    // Hacer clic en calcular rutas
    cy.get('[data-testid="calculate-button"]').click();
    
    // Verificar que se muestran los resultados
    cy.get('[data-testid="route-results"]').should('be.visible');
    cy.get('[data-testid="route-card"]').should('have.length.greaterThan', 0);
  });

  it('debería guardar una ruta calculada', () => {
    // Navegar a la página de cálculo de rutas
    cy.get('[data-testid="routes-link"]').click();
    
    // Llenar el formulario y calcular rutas
    cy.get('[data-testid="origin-input"]').type('Buenos Aires');
    cy.get('[data-testid="destination-input"]').type('Rosario');
    cy.get('[data-testid="vehicle-select"]').select('ABC123');
    cy.get('[data-testid="calculate-button"]').click();
    
    // Esperar a que se carguen los resultados
    cy.get('[data-testid="route-results"]').should('be.visible');
    
    // Guardar la primera ruta
    cy.get('[data-testid="save-route-button"]').first().click();
    
    // Verificar que se muestra mensaje de éxito
    cy.get('[data-testid="success-message"]').should('be.visible');
  });

  it('debería mostrar error cuando los campos están vacíos', () => {
    // Navegar a la página de cálculo de rutas
    cy.get('[data-testid="routes-link"]').click();
    
    // Hacer clic en calcular sin llenar campos
    cy.get('[data-testid="calculate-button"]').click();
    
    // Verificar que se muestran mensajes de error
    cy.get('[data-testid="error-message"]').should('be.visible');
  });
});