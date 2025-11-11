package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

var dataStore *DataStore
var validator *Validator

func main() {
	// Set up logging
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	log.Println("=================================================")
	log.Println("Qualifyze Verification and Analytics System")
	log.Println("=================================================")

	// Load CSV data on startup
	dataDir := "./data"
	if len(os.Args) > 1 {
		dataDir = os.Args[1]
	}

	var err error
	dataStore, err = LoadCSVData(dataDir)
	if err != nil {
		log.Fatalf("Failed to load CSV data: %v\n", err)
	}

	// Initialize validator
	validator = NewValidator(dataStore)

	// Set up HTTP routes
	http.HandleFunc("/api/load", handleLoadFile)
	http.HandleFunc("/api/validate", handleValidateAll)
	http.HandleFunc("/api/validate/request", handleValidateRequest)
	http.HandleFunc("/api/health", handleHealth)

	// Start server
	port := "8080"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	log.Printf("Starting server on port %s...\n", port)
	log.Println("=================================================")
	log.Println("Available endpoints:")
	log.Println("  GET  /api/health            - Health check")
	log.Println("  POST /api/load              - Reload CSV data")
	log.Println("  POST /api/validate          - Validate all requests")
	log.Println("  POST /api/validate/request  - Validate specific request")
	log.Println("=================================================")

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v\n", err)
	}
}

// handleHealth returns the health status of the API
func handleHealth(w http.ResponseWriter, r *http.Request) {
	log.Println("Health check requested")
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "healthy",
		"service": "Qualifyze Verification System",
	})
}

// handleLoadFile reloads CSV data from the data directory
func handleLoadFile(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	log.Println("Reload data requested via API")

	dataDir := "./data"
	if r.URL.Query().Get("dir") != "" {
		dataDir = r.URL.Query().Get("dir")
	}

	var err error
	dataStore, err = LoadCSVData(dataDir)
	if err != nil {
		log.Printf("Error reloading data: %v\n", err)
		http.Error(w, fmt.Sprintf("Failed to load data: %v", err), http.StatusInternalServerError)
		return
	}

	// Reinitialize validator with new data
	validator = NewValidator(dataStore)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "success",
		"message": "Data reloaded successfully",
		"stats": map[string]int{
			"requests":          len(dataStore.Requests),
			"credits":           len(dataStore.Credits),
			"suppliers":         len(dataStore.Suppliers),
			"quality_officers":  len(dataStore.QualityOfficers),
			"blacklist_entries": len(dataStore.SupplierBlacklist),
		},
	})

	log.Println("Data reloaded successfully via API")
}

// handleValidateAll validates all requests in the system
func handleValidateAll(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	log.Println("Validate all requests requested via API")

	results := make(map[string]ValidationResult)
	validCount := 0
	invalidCount := 0

	for _, request := range dataStore.Requests {
		result := validator.ValidateRequest(request)
		results[request.IDRequest] = result

		if result.Valid {
			validCount++
		} else {
			invalidCount++
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":          "success",
		"total_requests":  len(dataStore.Requests),
		"valid_requests":  validCount,
		"invalid_requests": invalidCount,
		"results":         results,
	})

	log.Printf("Validation complete: %d valid, %d invalid\n", validCount, invalidCount)
}

// handleValidateRequest validates a specific request by ID
func handleValidateRequest(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	requestID := r.URL.Query().Get("id")
	if requestID == "" {
		http.Error(w, "Request ID is required", http.StatusBadRequest)
		return
	}

	log.Printf("Validate request %s requested via API\n", requestID)

	// Find the request
	var targetRequest *Request
	for _, req := range dataStore.Requests {
		if req.IDRequest == requestID {
			targetRequest = &req
			break
		}
	}

	if targetRequest == nil {
		log.Printf("Request %s not found\n", requestID)
		http.Error(w, fmt.Sprintf("Request %s not found", requestID), http.StatusNotFound)
		return
	}

	result := validator.ValidateRequest(*targetRequest)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":     "success",
		"request_id": requestID,
		"result":     result,
	})

	log.Printf("Validation complete for request %s: valid=%v\n", requestID, result.Valid)
}
