package main

import (
	"encoding/json"
	"time"
)

// ContactInformation represents the contact details
type ContactInformation struct {
	Name    string `json:"name"`
	Surname string `json:"surname"`
	Email   string `json:"email"`
}

// Customer represents a customer who requests audits
type Customer struct {
	CustomerID         int
	AvailableCredits   int
	ContactInformation ContactInformation
}

// Supplier represents an audit executor
type Supplier struct {
	SupplierSiteID   int
	Site             string
	Address          string
	Contact          string
	Availability     bool
	Country          string
}

// InternalQA represents the internal quality assurance officer
type InternalQA struct {
	QualityOfficerID   int
	Owner              string
	Checklist          bool
	Flag               string
}

// Request represents an audit request
type Request struct {
	IDRequest              string
	CustomerID             int
	RequestDate            string
	RequestedStandard      string
	RequestedSupplierSiteID int
	RequestedAuditID       string
	AuditScope             string
	ContactInformation     ContactInformation
	QualityOfficerID       int
}

// Credit represents customer credit information
type Credit struct {
	CreditID     string
	CustomerID   int
	CreditState  string
	ReservedDate string
	ConsumedDate string
	IDRequest    string
}

// QualityOfficer represents an internal quality officer
type QualityOfficer struct {
	QualityOfficerID   int
	QualityOfficerName string
}

// SupplierBlacklist represents blacklisted suppliers
type SupplierBlacklist struct {
	SupplierSiteID   int
	BlacklistSince   string
	BlacklistUntil   string
}

// ValidationResult represents the result of validation
type ValidationResult struct {
	Valid    bool
	Warnings []string
	Errors   []string
}

// ParseContactInfo parses JSON contact information
func ParseContactInfo(contactJSON string) (ContactInformation, error) {
	var contact ContactInformation
	if contactJSON == "" {
		return contact, nil
	}
	err := json.Unmarshal([]byte(contactJSON), &contact)
	return contact, err
}

// IsDateInRange checks if today is within the blacklist date range
func IsDateInRange(since, until string) bool {
	now := time.Now()

	sinceDate, err := time.Parse("2006-01-02", since)
	if err != nil {
		return false
	}

	untilDate, err := time.Parse("2006-01-02", until)
	if err != nil {
		return false
	}

	return now.After(sinceDate) && now.Before(untilDate)
}
