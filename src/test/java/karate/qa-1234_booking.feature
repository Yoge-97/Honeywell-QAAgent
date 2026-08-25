Feature: QA-1234 - Guest Booking Form Submission

Background:
  Given the guest accesses the booking form

@TC-001
Scenario: TC-001: Fill all mandatory fields and submit the booking form
  When the guest fills all mandatory fields
  And submits the booking form
  Then the success message should be displayed

@TC-002
Scenario: TC-002: Leave the Name field empty and submit the booking form
  When the guest leaves the Name field empty
  And submits the booking form
  Then the success message should not be displayed

@TC-003
Scenario: TC-003: Leave the Number field empty and submit the booking form
  When the guest leaves the Number field empty
  And submits the booking form
  Then the success message should not be displayed