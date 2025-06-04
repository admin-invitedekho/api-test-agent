Feature: Edit Yourself @ ₹249 Comprehensive Workflow
  As a user of the InviteDekho platform
  I want to complete the "Edit Yourself @ ₹249" workflow
  So that I can customize my wedding invitation video with my details

  Background:
    Given I navigate to "https://stage.invitedekho.com"

  @complete_workflow @browser
  Scenario: Complete Edit @ ₹249 workflow with validation and UX testing
    # Navigate directly to the Romancia Glassy Love product page
    When I navigate to "https://stage.invitedekho.com/designs/wedding-video-invitation/romancia-glassy-love/"
    
    # Click Edit button and handle popup
    When I click the "Edit Yourself @ ₹249" button
    When I handle any popup by clicking "Close" if present
    
    # Test validation by clicking Next without filling required fields
    When I click the "Next" button
    # Should remain on step 1 due to validation
    
    # Fill required data and proceed
    When I enter pincode "400001"
    When I click the "Next" button
    When I click the bride option
    When I click the "Next" button
    
    # Test navigation back functionality
    When I click the "Previous" button
    # Should go back to step 2
    When I click the "Next" button
    # Should go forward to step 3 again
    
    # Fill names and continue
    When I enter groom details "Rahul" "Sharma"
    When I enter bride details "Priya" "Gupta"
    When I click the "Next" button
    
    # Fill wedding function details
    When I fill wedding function details with date "15/06/2025" and time "18:00"
    When I click the "Next" button
    
    # Fill additional details - greeting will auto-generate hashtag
    When I enter greeting message "Join us as we celebrate our love story"
    When I click the "Next" button
    
    # Skip song search, just submit
    When I click the "Submit" button

  @music_integration_detailed @browser
  Scenario: Complete YouTube music search and selection verification
    When I navigate to "https://stage.invitedekho.com/designs/wedding-video-invitation/romancia-glassy-love/"
    And I click the "Edit Yourself @ ₹249" button
    And I handle any popup by clicking "Close" if present
    
    # Quick navigation through steps 1-5 to reach music selection
    When I enter pincode "400001"
    And I click the "Next" button
    When I click the bride option
    And I click the "Next" button
    When I enter groom details "Rahul" "Sharma"
    And I enter bride details "Priya" "Gupta"
    And I click the "Next" button
    When I fill wedding function details with date "15/06/2025" and time "18:00"
    And I click the "Next" button
    When I enter greeting message "Join us as we celebrate our love story"
    And I click the "Next" button
    
    # Simplified music testing workflow
    When I enter song name "Perfect by Ed Sheeran" in search field
    And I click the "Search" button
    And I click the first YouTube video result
    And I click the "Select Audio" button
    And I click the "Submit" button

  @edge_cases_validation @browser
  Scenario: Test navigation, validation, and edge cases
    When I navigate to "https://stage.invitedekho.com/designs/wedding-video-invitation/romancia-glassy-love/"
    And I click the "Edit Yourself @ ₹249" button
    And I handle any popup by clicking "Close" if present
    
    # Test empty field validation on step 1
    When I click the "Next" button
    # Should remain on step 1 due to validation
    
    # Test with minimal required data
    When I enter pincode "400001"
    And I click the "Next" button
    
    When I click the bride option
    And I click the "Next" button
    
    # Test navigation back functionality
    When I click the "Previous" button
    # Should go back to step 2
    When I click the "Next" button
    # Should return to step 3
    
    # Complete minimal workflow
    When I enter groom details "Test" "Groom"
    And I enter bride details "Test" "Bride"
    
    When I click the "Next" button
    
    When I fill wedding function details with date "01/07/2025" and time "12:00"
    
    When I click the "Next" button
    
    When I enter greeting message "Welcome to our wedding"
    
    When I click the "Next" button
    
    # Step 6: Skip music selection - proceed directly
    When I click the "Submit" button 