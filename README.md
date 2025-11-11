# Qualyfize Verification and Analytics System

The following code process incoming requests ingested through an API using a csv file containing the information of each one.

## Requirements
- Code is written in Go Lang.
- API functions:
 - Load file
- If any rule is not accomplished a warning must be rised
- Every processing should be logged to console

## Classes
There are 3 classes of objects:
- Customer: Is the generator of each request. Ask for an Audit from the Suppliers.
- Supplier: Is the Audit executor, information contained is: Site, address, contact, availability.
- InternalQA: Is the internal owner of the audit process, information contained is: Owner, Checklist, Flag

## Verification Logic Flow
The following is a Mermaid Flowchart of the validation process

```mermaid
flowchart
    A([Request Submited]) --> B[Customer Request Validation]
    subgraph Customer_Validation[Customer Validation]
        B --> B1{Customer info complete?}
        B1 -->|Yes| B2{Credits Available?}
        B1 -->|No| R1[Return to customer indicate missing value]
        B2 -->|No| R2[Hold request and indicate customer to buy credits]
        R2 --> B2
        B2 -->|Yes| B3[Next Step]
    end
    B3 --> C[Supplier Request Validation]
    subgraph Supplier Validation[Supplier Validation]
    C --> C1{Supplier info complete?}
    C1 -->|Yes| C2{Is Supplier Blacklisted?}
    C1 -->|No| C3[Return to Supplier]
    C2 -->|Yes| C4[Alert Customer!?]
C4 --> R3[Ask customer to modify Supplier]
    C2 -->|No| C5[Next Step]
end
C5 --> D[IQ Validation]
subgraph IQ Request Validation[Internal Quality Validation]
D --> D1{IQ info complete?}
D -->|No| D2[Return To IQ to complete]
D2 --> D1
D1 -->|Yes| E[Request Valid]
end
E --> F([Process Request])
```

