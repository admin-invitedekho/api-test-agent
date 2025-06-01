Feature: User Profile Verification
  As a user of the InviteDekho platform
  I want to verify my profile information after login
  So that I can ensure my account details are correct

  Scenario: Step-by-step user profile verification
    # Navigation
    Given I open browser and navigate to "https://stage.invitedekho.com"
    
    # Login Process
    When I click the "Login" button with reference "e58"
    And I click "Sign in with Email" button with reference "e22"
    And I fill "admin@invitedekho.com" into "Email Address" textbox with reference "e37"
    And I fill "Test@123456" into "Password" textbox with reference "e42"
    And I click "Sign in" button with reference "e47"
    
    # Post-Login Navigation
    Then I wait for 3 seconds for login to complete
    And I should be on homepage with URL "https://stage.invitedekho.com/"
    
    # Access User Profile
    When I click user icon button with reference "e118"
    And I click "Profile" menu item with reference "e1051"
    
    # Verify Profile Information
    Then I should be on "/profile/" page
    And I should see the following profile data:
      """
      First Name: Vibhor
      Last Name: Goyal
      Email: admin@invitedekho.com
      Phone: 9412817667
      """
    
    # Documentation
    When I take a screenshot named "user-profile-info.png"
    Then the verification process is complete 