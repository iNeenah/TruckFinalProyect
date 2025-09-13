describe('Authentication Flow', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'password123',
    firstName: 'Test',
    lastName: 'User'
  };

  beforeEach(() => {
    // Reset database or mock API responses
    cy.visit('/');
  });

  it('should allow a user to register and login', () => {
    // Navigate to register page
    cy.visit('/register');
    
    // Fill registration form
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('input[name="full_name"]').type(`${testUser.firstName} ${testUser.lastName}`);
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, Test User');
  });

  it('should allow a user to login with existing credentials', () => {
    // Navigate to login page
    cy.visit('/login');
    
    // Fill login form
    cy.get('input[name="email"]').type(testUser.email);
    cy.get('input[name="password"]').type(testUser.password);
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, Test User');
  });

  it('should show error for invalid credentials', () => {
    cy.visit('/login');
    
    cy.get('input[name="email"]').type('invalid@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    
    cy.contains('Invalid credentials').should('be.visible');
  });

  it('should allow user to logout', () => {
    // First login
    cy.login(testUser.email, testUser.password);
    
    // Click user menu and logout
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="logout-button"]').click();
    
    // Should redirect to login page
    cy.url().should('include', '/login');
  });
});