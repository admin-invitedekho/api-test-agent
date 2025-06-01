Feature: User Profile Verification
  As a user of the InviteDekho platform
  I want to verify my profile information after login
  So that I can ensure my account details are correct

  Scenario: Complete user profile verification workflow
    # Navigate to the website
    Given I open my browser and go to "https://stage.invitedekho.com"
    
    # Login to my account
    When I click on the "Login" button
    And I choose "Sign in with Email" option
    And I enter "admin@invitedekho.com" in the email field
    And I enter "Test@123456" in the password field
    And I click the "Sign in" button to log in
    
    # Wait for login to complete
    Then I should wait for the page to load completely
    And I should be logged in and see the homepage
    
    # Navigate to my profile
    When I click on the user menu icon
    And I select "Profile" from the dropdown menu
    
    # Verify my profile information is correct
    Then I should be on my profile page
    And I should see my personal information displayed correctly:
      """
      First Name: Vibhor
      Last Name: Goyal
      Email: admin@invitedekho.com
      Phone: 9412817667
      """