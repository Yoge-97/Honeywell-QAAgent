Feature: QA-1234 - Guest Booking Form Submission

Background:
  * url baseUrl
  * path '/booking'

Scenario: TC-001 - Fill all mandatory fields and submit the booking form
  Given request { name: 'John Doe', number: '1234567890' }
  When method post
  Then status 200
  And match response.message == '#present'

Scenario: TC-002 - Leave the Name field empty and submit the booking form
  Given request { name: '', number: '1234567890' }
  When method post
  Then status 400
  And match response.message != '#present'

Scenario: TC-003 - Leave the Number field empty and submit the booking form
  Given request { name: 'John Doe', number: '' }
  When method post
  Then status 400
  And match response.message != '#present'