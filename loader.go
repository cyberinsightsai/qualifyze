package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

// DataStore holds all loaded data
type DataStore struct {
	Requests          []Request
	Credits           []Credit
	Suppliers         []Supplier
	QualityOfficers   []QualityOfficer
	SupplierBlacklist []SupplierBlacklist
}

// LoadCSVData loads all CSV files and returns a DataStore
func LoadCSVData(dataDir string) (*DataStore, error) {
	log.Println("Starting to load CSV data from directory:", dataDir)

	ds := &DataStore{}
	var err error

	// Load requests
	log.Println("Loading data_requests.csv...")
	ds.Requests, err = loadRequests(dataDir + "/data_requests.csv")
	if err != nil {
		return nil, fmt.Errorf("error loading requests: %w", err)
	}
	log.Printf("Loaded %d requests\n", len(ds.Requests))

	// Load credits
	log.Println("Loading credits.csv...")
	ds.Credits, err = loadCredits(dataDir + "/credits.csv")
	if err != nil {
		return nil, fmt.Errorf("error loading credits: %w", err)
	}
	log.Printf("Loaded %d credits\n", len(ds.Credits))

	// Load suppliers
	log.Println("Loading suppliers.csv...")
	ds.Suppliers, err = loadSuppliers(dataDir + "/suppliers.csv")
	if err != nil {
		return nil, fmt.Errorf("error loading suppliers: %w", err)
	}
	log.Printf("Loaded %d suppliers\n", len(ds.Suppliers))

	// Load quality officers
	log.Println("Loading quality_officers.csv...")
	ds.QualityOfficers, err = loadQualityOfficers(dataDir + "/quality_officers.csv")
	if err != nil {
		return nil, fmt.Errorf("error loading quality officers: %w", err)
	}
	log.Printf("Loaded %d quality officers\n", len(ds.QualityOfficers))

	// Load supplier blacklist
	log.Println("Loading supplier_blacklist.csv...")
	ds.SupplierBlacklist, err = loadSupplierBlacklist(dataDir + "/supplier_blacklist.csv")
	if err != nil {
		return nil, fmt.Errorf("error loading supplier blacklist: %w", err)
	}
	log.Printf("Loaded %d blacklisted suppliers\n", len(ds.SupplierBlacklist))

	log.Println("Successfully loaded all CSV data")
	return ds, nil
}

func loadRequests(filename string) ([]Request, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var requests []Request
	for i, record := range records {
		if i == 0 {
			continue // Skip header
		}

		customerID, _ := strconv.Atoi(record[1])
		supplierSiteID, _ := strconv.Atoi(record[4])
		qualityOfficerID, _ := strconv.Atoi(record[8])

		contact, _ := ParseContactInfo(record[7])

		request := Request{
			IDRequest:              record[0],
			CustomerID:             customerID,
			RequestDate:            record[2],
			RequestedStandard:      record[3],
			RequestedSupplierSiteID: supplierSiteID,
			RequestedAuditID:       record[5],
			AuditScope:             record[6],
			ContactInformation:     contact,
			QualityOfficerID:       qualityOfficerID,
		}
		requests = append(requests, request)
	}

	return requests, nil
}

func loadCredits(filename string) ([]Credit, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var credits []Credit
	for i, record := range records {
		if i == 0 {
			continue // Skip header
		}

		customerID, _ := strconv.Atoi(record[1])

		credit := Credit{
			CreditID:     record[0],
			CustomerID:   customerID,
			CreditState:  record[2],
			ReservedDate: record[3],
			ConsumedDate: record[4],
			IDRequest:    record[5],
		}
		credits = append(credits, credit)
	}

	return credits, nil
}

func loadSuppliers(filename string) ([]Supplier, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var suppliers []Supplier
	for i, record := range records {
		if i == 0 {
			continue // Skip header
		}

		supplierSiteID, _ := strconv.Atoi(record[0])
		availability := strings.ToUpper(record[4]) == "TRUE"

		supplier := Supplier{
			SupplierSiteID: supplierSiteID,
			Site:           record[1],
			Country:        record[2],
			Address:        record[3],
			Availability:   availability,
		}
		suppliers = append(suppliers, supplier)
	}

	return suppliers, nil
}

func loadQualityOfficers(filename string) ([]QualityOfficer, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var officers []QualityOfficer
	for i, record := range records {
		if i == 0 {
			continue // Skip header
		}

		qualityOfficerID, _ := strconv.Atoi(record[0])

		officer := QualityOfficer{
			QualityOfficerID:   qualityOfficerID,
			QualityOfficerName: record[1],
		}
		officers = append(officers, officer)
	}

	return officers, nil
}

func loadSupplierBlacklist(filename string) ([]SupplierBlacklist, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var blacklist []SupplierBlacklist
	for i, record := range records {
		if i == 0 {
			continue // Skip header
		}

		supplierSiteID, _ := strconv.Atoi(record[0])

		entry := SupplierBlacklist{
			SupplierSiteID:   supplierSiteID,
			BlacklistSince:   record[1],
			BlacklistUntil:   record[2],
		}
		blacklist = append(blacklist, entry)
	}

	return blacklist, nil
}
