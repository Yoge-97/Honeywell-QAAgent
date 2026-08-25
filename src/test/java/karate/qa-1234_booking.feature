Feature: QA-1234 - Booking Form Submission
  As a guest, I want to submit the booking form so that I can complete my booking.

Background:
  * url baseUrl

@TC-001
Scenario: TC-001 - Fill all mandatory fields and submit the booking form
  Given path '/booking'
  And request { name: 'John Doe', number: '1234567890' }
  When method post
  Then status 200
  And match response.message == '#present'

@TC-002
Scenario: TC-002 - Leave the Name field empty and submit the booking form
  Given path '/booking'
  And request { name: '', number: '1234567890' }
  When method post
  Then status 400
  And match response.message == '#notpresent'

@TC-003
Scenario: TC-003 - Leave the Number field empty and submit the booking form
  Given path '/booking'
  And request { name: 'John Doe', number: '' }
  When method post
  Then status 400
  And match response.message == '#notpresent'