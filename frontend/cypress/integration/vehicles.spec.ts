describe('Vehicle Management', () => {
  const testVehicle = {
    name: 'Test Truck',
    licensePlate: 'TEST123',
    fuelType: 'diesel',
    fuelConsumption: 8.5
  };

  beforeEach(() => {
    // Login before each test
    cy.login('test@example.com', 'password123');
    cy.visit('/vehicles');
  });

  it('should display empty state when no vehicles exist', () => {
    // Assuming we're testing with a clean state
    cy.contains('No vehicles').should('be.visible');
    cy.contains('Add Vehicle').should('be.visible');
  });

  it('should allow creating a new vehicle', () => {
    // Click add vehicle button
    cy.get('[data-testid="add-vehicle-button"]').click();
    
    // Fill vehicle form
    cy.get('input[name="name"]').type(testVehicle.name);
    cy.get('input[name="license_plate"]').type(testVehicle.licensePlate);
    cy.get('select[name="fuel_type"]').select(testVehicle.fuelType);
    cy.get('input[name="fuel_consumption"]').type(testVehicle.fuelConsumption.toString());
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Should show success message and vehicle in list
    cy.contains('Vehicle created successfully').should('be.visible');
    cy.contains(testVehicle.name).should('be.visible');
    cy.contains(testVehicle.licensePlate).should('be.visible');
  });

  it('should allow editing an existing vehicle', () => {
    // Create a vehicle first if needed
    cy.createVehicle(testVehicle);
    
    // Find the vehicle in the list and click edit
    cy.contains(testVehicle.name).parents('tr').find('[data-testid="edit-button"]').click();
    
    // Modify vehicle data
    const updatedName = 'Updated Test Truck';
    cy.get('input[name="name"]').clear().type(updatedName);
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Should show success message and updated vehicle
    cy.contains('Vehicle updated successfully').should('be.visible');
    cy.contains(updatedName).should('be.visible');
  });

  it('should allow deleting a vehicle', () => {
    // Create a vehicle first if needed
    cy.createVehicle(testVehicle);
    
    // Find the vehicle in the list and click delete
    cy.contains(testVehicle.name).parents('tr').find('[data-testid="delete-button"]').click();
    
    // Confirm deletion
    cy.contains('Are you sure?').should('be.visible');
    cy.get('[data-testid="confirm-delete"]').click();
    
    // Should show success message and vehicle should be gone
    cy.contains('Vehicle deleted successfully').should('be.visible');
    cy.contains(testVehicle.name).should('not.exist');
  });

  it('should allow filtering vehicles by status', () => {
    // Create active and inactive vehicles
    cy.createVehicle({...testVehicle, name: 'Active Vehicle'});
    
    // Create an inactive vehicle (implementation depends on your app)
    // ...
    
    // Filter by active vehicles
    cy.get('select[name="status"]').select('active');
    cy.contains('Active Vehicle').should('be.visible');
    
    // Filter by inactive vehicles
    cy.get('select[name="status"]').select('inactive');
    // Check for inactive vehicles
  });
});