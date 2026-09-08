Feature: QA-1003 - Checkout

  Background:
    * url baseUrl
    * path '/checkout'

  @TC-001
  Scenario: Checkout with valid order details
    Given request { productId: 'P1001', quantity: 1 }
    When method post
    Then status 200

  @TC-002
  Scenario: Checkout with invalid product
    Given request { productId: 'INVALID', quantity: 1 }
    When method post
    Then status 404

  @TC-003
  Scenario: Checkout with zero quantity
    Given request { productId: 'P1001', quantity: 0 }
    When method post
    Then status 400
