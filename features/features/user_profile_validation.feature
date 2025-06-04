Feature: User Profile Data Validation - UI vs API
  As a QA engineer
  I want to validate that user profile data is consistent between UI and API
  So that I can ensure data integrity across different interfaces

  @mixed @profile_validation
  Scenario: Validate user profile data consistency between UI and API
    # Step 1: Navigate to base URL
    Given I navigate to "https://stage.invitedekho.com"
    
    # Step 2: Login through UI (this will also login via API to get the auth token)
    When I click on the "Login" link in the header
    And I enter email "admin@invitedekho.com" in the email field
    And I enter password "Test@123456" in the password field
    And I click the "Login" button to submit the form
    And I login to the API with email "admin@invitedekho.com" and password "Test@123456"
    
    # Step 3: Extract JWT token from the API login response (for subsequent API calls)
    When I extract the authentication token from the login response
    
    # Step 4: Navigate to user profile page through UI
    When I click on the user profile icon in the top right corner
    And I click on "Profile" in the dropdown menu
    
    # Step 5: Capture profile data from UI
    When I capture user profile data from the UI including name, email, and phone
    
    # Step 6: Get user data from API using the extracted token
    When I make a GET request to "http://api.stage.invitedekho.com/user/me"
    
    # Step 7: Validate data consistency between UI and API
    Then the API response should contain valid user data
    And the user email from API should match the UI displayed email
    And the user name from API should match the UI displayed name
    And the user phone from API should match the UI displayed phone
    And the API response should have the correct JSON structure
    
    # Step 8: Validate API response structure and required fields
    Then the API response should contain field "email" with valid email format
    And the API response should contain field "name" that is not empty
    And the API response should contain field "phone" with valid phone format
    And the response status code should be 200
    
    # Step 9: Additional data validation
    When I verify that all mandatory profile fields are populated in both UI and API
    Then the data integrity check should pass for all user profile fields 