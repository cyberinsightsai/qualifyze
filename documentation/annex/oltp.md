# OLTP ER 

````mermaid
erDiagram
    REQUESTS {
        int id_request PK
        int customer_id
        int supplier_id FK
        date request_date
        string requested_standard "GMP|GVP|GCP"
        string requested_supplier_site_id
        string requested_audit_id
        string audit_scope
        string contact_information
        string quality_officer_id
    }

  
    SUPPLIERS {
        int supplier_site_id PK
        string supplier_site_name
        string supplier_site_country
        string supplier_site_address
        string contact_details
        boolean supplier_site_availability 
    }


    SUPPLIER_BLACKLIST {
        int supplier_site_id PK
        date blacklist_since
        date blacklist_until
    }
  
    CREDITS {
        string credit_id PK
        string customer_id
        string credit_state "available|reserved|consumed"
        date reserved_date
        date consumed_date
        string id_request
    }

    QUALITY_OFFICERS {
        int quality_officer_id PK
        string quality_officer_name
    }
  
    %% Relationships
    SUPPLIERS ||--o{ REQUESTS : ""
    SUPPLIER_BLACKLIST }o--|| SUPPLIERS : ""
    CREDITS ||--o{ REQUESTS : ""
    QUALITY_OFFICERS ||--o{ REQUESTS : ""
```