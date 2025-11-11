package main

import (
	"fmt"
	"log"
)

// Validator handles all validation logic
type Validator struct {
	dataStore *DataStore
}

// NewValidator creates a new Validator instance
func NewValidator(ds *DataStore) *Validator {
	return &Validator{dataStore: ds}
}

// ValidateRequest validates a request following the flowchart logic
func (v *Validator) ValidateRequest(request Request) ValidationResult {
	result := ValidationResult{
		Valid:    true,
		Warnings: []string{},
		Errors:   []string{},
	}

	log.Printf("Starting validation for request: %s\n", request.IDRequest)

	// Step 1: Customer Validation
	log.Println("Step 1: Customer Validation")
	customerValid := v.validateCustomer(request, &result)
	if !customerValid {
		log.Printf("Request %s failed customer validation\n", request.IDRequest)
		return result
	}

	// Step 2: Supplier Validation
	log.Println("Step 2: Supplier Validation")
	supplierValid := v.validateSupplier(request, &result)
	if !supplierValid {
		log.Printf("Request %s failed supplier validation\n", request.IDRequest)
		return result
	}

	// Step 3: Internal QA Validation
	log.Println("Step 3: Internal QA Validation")
	iqValid := v.validateInternalQA(request, &result)
	if !iqValid {
		log.Printf("Request %s failed internal QA validation\n", request.IDRequest)
		return result
	}

	log.Printf("Request %s passed all validations!\n", request.IDRequest)
	return result
}

// validateCustomer validates customer information and credits
func (v *Validator) validateCustomer(request Request, result *ValidationResult) bool {
	log.Printf("Validating customer %d for request %s\n", request.CustomerID, request.IDRequest)

	// Check if customer info is complete
	if request.CustomerID == 0 {
		result.Valid = false
		result.Errors = append(result.Errors, "Customer ID is missing")
		log.Println("WARNING: Customer ID is missing")
		return false
	}

	if request.ContactInformation.Name == "" || request.ContactInformation.Email == "" {
		result.Valid = false
		result.Errors = append(result.Errors, "Customer contact information is incomplete")
		log.Println("WARNING: Customer contact information is incomplete")
		return false
	}

	// Check if credits are available
	availableCredits := v.getAvailableCredits(request.CustomerID)
	log.Printf("Customer %d has %d available credits\n", request.CustomerID, availableCredits)

	if availableCredits <= 0 {
		result.Valid = false
		result.Errors = append(result.Errors, fmt.Sprintf("Customer %d has no available credits. Please purchase credits.", request.CustomerID))
		log.Printf("WARNING: Customer %d has no available credits\n", request.CustomerID)
		return false
	}

	log.Printf("Customer validation passed for customer %d\n", request.CustomerID)
	return true
}

// validateSupplier validates supplier information and blacklist status
func (v *Validator) validateSupplier(request Request, result *ValidationResult) bool {
	log.Printf("Validating supplier %d for request %s\n", request.RequestedSupplierSiteID, request.IDRequest)

	// Check if supplier info is complete
	if request.RequestedSupplierSiteID == 0 {
		result.Valid = false
		result.Errors = append(result.Errors, "Supplier site ID is missing")
		log.Println("WARNING: Supplier site ID is missing")
		return false
	}

	// Find supplier in database
	supplier := v.findSupplier(request.RequestedSupplierSiteID)
	if supplier == nil {
		result.Valid = false
		result.Errors = append(result.Errors, fmt.Sprintf("Supplier site ID %d not found in database", request.RequestedSupplierSiteID))
		log.Printf("WARNING: Supplier site ID %d not found\n", request.RequestedSupplierSiteID)
		return false
	}

	// Check if supplier information is complete
	if supplier.Site == "" || supplier.Address == "" {
		result.Valid = false
		result.Errors = append(result.Errors, fmt.Sprintf("Supplier %d has incomplete information", request.RequestedSupplierSiteID))
		log.Printf("WARNING: Supplier %d has incomplete information\n", request.RequestedSupplierSiteID)
		return false
	}

	// Check if supplier is available
	if !supplier.Availability {
		result.Warnings = append(result.Warnings, fmt.Sprintf("Supplier %d (%s) is currently not available", supplier.SupplierSiteID, supplier.Site))
		log.Printf("WARNING: Supplier %d is not available\n", supplier.SupplierSiteID)
	}

	// Check if supplier is blacklisted
	if v.isSupplierBlacklisted(request.RequestedSupplierSiteID) {
		result.Valid = false
		result.Errors = append(result.Errors, fmt.Sprintf("ALERT: Supplier %d (%s) is currently blacklisted! Customer must modify supplier.", supplier.SupplierSiteID, supplier.Site))
		log.Printf("ALERT: Supplier %d is blacklisted!\n", supplier.SupplierSiteID)
		return false
	}

	log.Printf("Supplier validation passed for supplier %d\n", request.RequestedSupplierSiteID)
	return true
}

// validateInternalQA validates internal quality assurance information
func (v *Validator) validateInternalQA(request Request, result *ValidationResult) bool {
	log.Printf("Validating internal QA officer %d for request %s\n", request.QualityOfficerID, request.IDRequest)

	// Check if quality officer is assigned
	if request.QualityOfficerID == 0 {
		result.Valid = false
		result.Errors = append(result.Errors, "Quality officer is not assigned. Please assign a quality officer to complete the request.")
		log.Println("WARNING: Quality officer is not assigned")
		return false
	}

	// Find quality officer in database
	officer := v.findQualityOfficer(request.QualityOfficerID)
	if officer == nil {
		result.Valid = false
		result.Errors = append(result.Errors, fmt.Sprintf("Quality officer ID %d not found in database", request.QualityOfficerID))
		log.Printf("WARNING: Quality officer ID %d not found\n", request.QualityOfficerID)
		return false
	}

	// Check if request has required fields for IQ processing
	if request.RequestedStandard == "" {
		result.Valid = false
		result.Errors = append(result.Errors, "Requested standard is missing. Internal QA cannot process without this information.")
		log.Println("WARNING: Requested standard is missing")
		return false
	}

	log.Printf("Internal QA validation passed. Officer: %s (ID: %d)\n", officer.QualityOfficerName, officer.QualityOfficerID)
	return true
}

// Helper functions

func (v *Validator) getAvailableCredits(customerID int) int {
	count := 0
	for _, credit := range v.dataStore.Credits {
		if credit.CustomerID == customerID && credit.CreditState == "available" {
			count++
		}
	}
	return count
}

func (v *Validator) findSupplier(supplierSiteID int) *Supplier {
	for _, supplier := range v.dataStore.Suppliers {
		if supplier.SupplierSiteID == supplierSiteID {
			return &supplier
		}
	}
	return nil
}

func (v *Validator) isSupplierBlacklisted(supplierSiteID int) bool {
	for _, blacklist := range v.dataStore.SupplierBlacklist {
		if blacklist.SupplierSiteID == supplierSiteID {
			// Check if current date is within blacklist period
			if IsDateInRange(blacklist.BlacklistSince, blacklist.BlacklistUntil) {
				return true
			}
		}
	}
	return false
}

func (v *Validator) findQualityOfficer(qualityOfficerID int) *QualityOfficer {
	for _, officer := range v.dataStore.QualityOfficers {
		if officer.QualityOfficerID == qualityOfficerID {
			return &officer
		}
	}
	return nil
}

// ValidateAllRequests validates all requests in the data store
func (v *Validator) ValidateAllRequests() {
	log.Println("=================================================")
	log.Println("Starting validation of all requests")
	log.Println("=================================================")

	validCount := 0
	invalidCount := 0

	for _, request := range v.dataStore.Requests {
		log.Println("\n-------------------------------------------------")
		result := v.ValidateRequest(request)

		if result.Valid {
			validCount++
			log.Printf("✓ Request %s is VALID\n", request.IDRequest)
		} else {
			invalidCount++
			log.Printf("✗ Request %s is INVALID\n", request.IDRequest)
		}

		if len(result.Warnings) > 0 {
			log.Println("Warnings:")
			for _, warning := range result.Warnings {
				log.Printf("  - %s\n", warning)
			}
		}

		if len(result.Errors) > 0 {
			log.Println("Errors:")
			for _, err := range result.Errors {
				log.Printf("  - %s\n", err)
			}
		}
	}

	log.Println("\n=================================================")
	log.Println("Validation Summary")
	log.Println("=================================================")
	log.Printf("Total requests: %d\n", len(v.dataStore.Requests))
	log.Printf("Valid requests: %d\n", validCount)
	log.Printf("Invalid requests: %d\n", invalidCount)
	log.Println("=================================================")
}
