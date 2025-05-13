# Component Diagram

This document provides visual representations of the GEO-INFER-INTRA system architecture using component diagrams.

## System Overview

The following diagram shows the high-level components of the GEO-INFER-INTRA system and their relationships:

```mermaid
graph TB
    subgraph "User Interfaces"
        UI[Web Interface]
        CLI[Command Line Interface]
        API_CLIENTS[API Clients]
    end

    subgraph "API Layer"
        API_GATEWAY[API Gateway]
        AUTH[Authentication & Authorization]
        RATE_LIMIT[Rate Limiting]
    end
    
    subgraph "Core Services"
        DOC_SERVICE[Documentation Service]
        KB_SERVICE[Knowledge Base Service]
        ONTO_SERVICE[Ontology Service]
        WORKFLOW_SERVICE[Workflow Service]
    end
    
    subgraph "Storage"
        DOC_STORE[Documentation Store]
        KB_STORE[Knowledge Base Store]
        ONTO_STORE[Ontology Store]
        WORKFLOW_STORE[Workflow Store]
        USER_STORE[User Store]
    end
    
    subgraph "External Integration"
        INTEGRATION[Integration Services]
        MESSAGING[Messaging System]
    end
    
    UI --> API_GATEWAY
    CLI --> API_GATEWAY
    API_CLIENTS --> API_GATEWAY
    
    API_GATEWAY --> AUTH
    API_GATEWAY --> RATE_LIMIT
    
    AUTH --> DOC_SERVICE
    AUTH --> KB_SERVICE
    AUTH --> ONTO_SERVICE
    AUTH --> WORKFLOW_SERVICE
    
    DOC_SERVICE --> DOC_STORE
    KB_SERVICE --> KB_STORE
    ONTO_SERVICE --> ONTO_STORE
    WORKFLOW_SERVICE --> WORKFLOW_STORE
    
    AUTH --> USER_STORE
    
    DOC_SERVICE --> INTEGRATION
    KB_SERVICE --> INTEGRATION
    ONTO_SERVICE --> INTEGRATION
    WORKFLOW_SERVICE --> INTEGRATION
    
    INTEGRATION --> MESSAGING
    
    classDef primary fill:#f9f,stroke:#333,stroke-width:2px
    classDef secondary fill:#bbf,stroke:#333,stroke-width:1px
    classDef storage fill:#dfd,stroke:#333,stroke-width:1px
    classDef external fill:#ffd,stroke:#333,stroke-width:1px
    
    class UI,CLI,API_CLIENTS primary
    class API_GATEWAY,AUTH,RATE_LIMIT,DOC_SERVICE,KB_SERVICE,ONTO_SERVICE,WORKFLOW_SERVICE secondary
    class DOC_STORE,KB_STORE,ONTO_STORE,WORKFLOW_STORE,USER_STORE storage
    class INTEGRATION,MESSAGING external
```

## Documentation System Components

Detailed view of the Documentation Service components:

```mermaid
graph TB
    subgraph "Documentation Service"
        DOC_API[Documentation API]
        DOC_PROCESSOR[Documentation Processor]
        DOC_SEARCH[Search Engine]
        DOC_RENDERER[Documentation Renderer]
        VERSION_CONTROL[Version Control]
    end
    
    subgraph "Storage"
        MD_FILES[Markdown Files]
        ASSETS[Images & Assets]
        INDEX_DB[Search Index]
        VERSION_DB[Version Database]
    end
    
    DOC_API --> DOC_PROCESSOR
    DOC_API --> DOC_SEARCH
    DOC_API --> DOC_RENDERER
    DOC_API --> VERSION_CONTROL
    
    DOC_PROCESSOR --> MD_FILES
    DOC_PROCESSOR --> ASSETS
    
    DOC_SEARCH --> INDEX_DB
    
    DOC_RENDERER --> MD_FILES
    DOC_RENDERER --> ASSETS
    
    VERSION_CONTROL --> VERSION_DB
    VERSION_CONTROL --> MD_FILES
    
    classDef service fill:#bbf,stroke:#333,stroke-width:1px
    classDef store fill:#dfd,stroke:#333,stroke-width:1px
    
    class DOC_API,DOC_PROCESSOR,DOC_SEARCH,DOC_RENDERER,VERSION_CONTROL service
    class MD_FILES,ASSETS,INDEX_DB,VERSION_DB store
```

## Knowledge Base Components

Detailed view of the Knowledge Base Service components:

```mermaid
graph TB
    subgraph "Knowledge Base Service"
        KB_API[Knowledge Base API]
        KB_SEARCH[Full-text Search]
        KB_INDEXER[Content Indexer]
        KB_VALIDATOR[Content Validator]
        KB_RECOMMENDER[Recommender System]
    end
    
    subgraph "Storage"
        ARTICLES[Knowledge Articles]
        SEARCH_INDEX[Search Index]
        TAXONOMY[Category Taxonomy]
        USER_DATA[User Interaction Data]
    end
    
    KB_API --> KB_SEARCH
    KB_API --> KB_INDEXER
    KB_API --> KB_VALIDATOR
    KB_API --> KB_RECOMMENDER
    
    KB_SEARCH --> SEARCH_INDEX
    
    KB_INDEXER --> ARTICLES
    KB_INDEXER --> SEARCH_INDEX
    
    KB_VALIDATOR --> ARTICLES
    KB_VALIDATOR --> TAXONOMY
    
    KB_RECOMMENDER --> ARTICLES
    KB_RECOMMENDER --> USER_DATA
    
    classDef service fill:#bbf,stroke:#333,stroke-width:1px
    classDef store fill:#dfd,stroke:#333,stroke-width:1px
    
    class KB_API,KB_SEARCH,KB_INDEXER,KB_VALIDATOR,KB_RECOMMENDER service
    class ARTICLES,SEARCH_INDEX,TAXONOMY,USER_DATA store
```

## Ontology Management Components

Detailed view of the Ontology Service components:

```mermaid
graph TB
    subgraph "Ontology Service"
        ONTO_API[Ontology API]
        ONTO_PARSER[Ontology Parser]
        ONTO_VALIDATOR[Ontology Validator]
        ONTO_REASONER[Reasoner]
        ONTO_MAPPER[Cross-Domain Mapper]
    end
    
    subgraph "Storage"
        ONTOLOGIES[Ontology Files]
        MAPPING_RULES[Mapping Rules]
        VALIDATION_RULES[Validation Rules]
    end
    
    ONTO_API --> ONTO_PARSER
    ONTO_API --> ONTO_VALIDATOR
    ONTO_API --> ONTO_REASONER
    ONTO_API --> ONTO_MAPPER
    
    ONTO_PARSER --> ONTOLOGIES
    
    ONTO_VALIDATOR --> ONTOLOGIES
    ONTO_VALIDATOR --> VALIDATION_RULES
    
    ONTO_REASONER --> ONTOLOGIES
    
    ONTO_MAPPER --> ONTOLOGIES
    ONTO_MAPPER --> MAPPING_RULES
    
    classDef service fill:#bbf,stroke:#333,stroke-width:1px
    classDef store fill:#dfd,stroke:#333,stroke-width:1px
    
    class ONTO_API,ONTO_PARSER,ONTO_VALIDATOR,ONTO_REASONER,ONTO_MAPPER service
    class ONTOLOGIES,MAPPING_RULES,VALIDATION_RULES store
```

## Workflow System Components

Detailed view of the Workflow Service components:

```mermaid
graph TB
    subgraph "Workflow Service"
        WF_API[Workflow API]
        WF_DESIGNER[Workflow Designer]
        WF_ENGINE[Workflow Engine]
        WF_MONITOR[Execution Monitor]
        WF_SCHEDULER[Scheduler]
    end
    
    subgraph "Storage"
        WF_TEMPLATES[Workflow Templates]
        WF_INSTANCES[Workflow Instances]
        WF_LOGS[Execution Logs]
        WF_REGISTRY[Node Registry]
    end
    
    WF_API --> WF_DESIGNER
    WF_API --> WF_ENGINE
    WF_API --> WF_MONITOR
    WF_API --> WF_SCHEDULER
    
    WF_DESIGNER --> WF_TEMPLATES
    WF_DESIGNER --> WF_REGISTRY
    
    WF_ENGINE --> WF_TEMPLATES
    WF_ENGINE --> WF_INSTANCES
    WF_ENGINE --> WF_LOGS
    
    WF_MONITOR --> WF_INSTANCES
    WF_MONITOR --> WF_LOGS
    
    WF_SCHEDULER --> WF_TEMPLATES
    WF_SCHEDULER --> WF_INSTANCES
    
    classDef service fill:#bbf,stroke:#333,stroke-width:1px
    classDef store fill:#dfd,stroke:#333,stroke-width:1px
    
    class WF_API,WF_DESIGNER,WF_ENGINE,WF_MONITOR,WF_SCHEDULER service
    class WF_TEMPLATES,WF_INSTANCES,WF_LOGS,WF_REGISTRY store
```

## Integration with Other GEO-INFER Modules

The following diagram shows how GEO-INFER-INTRA integrates with other modules in the GEO-INFER framework:

```mermaid
graph LR
    subgraph "GEO-INFER-INTRA"
        INTRA_API[API Layer]
        INTRA_CORE[Core Services]
    end
    
    subgraph "GEO-INFER-SPACE"
        SPACE_API[Spatial API]
        SPACE_CORE[Spatial Services]
    end
    
    subgraph "GEO-INFER-TIME"
        TIME_API[Temporal API]
        TIME_CORE[Temporal Services]
    end
    
    subgraph "GEO-INFER-API"
        API_GATEWAY[API Gateway]
    end
    
    subgraph "GEO-INFER-APP"
        APP_UI[User Interfaces]
    end
    
    subgraph "GEO-INFER-OPS"
        OPS_CORE[Operational Services]
    end
    
    INTRA_API <--> SPACE_API
    INTRA_API <--> TIME_API
    INTRA_API <--> API_GATEWAY
    
    INTRA_CORE --> APP_UI
    
    OPS_CORE --> INTRA_CORE
    OPS_CORE --> SPACE_CORE
    OPS_CORE --> TIME_CORE
    
    API_GATEWAY --> APP_UI
    
    classDef intra fill:#f9f,stroke:#333,stroke-width:2px
    classDef space fill:#bbf,stroke:#333,stroke-width:1px
    classDef time fill:#dfd,stroke:#333,stroke-width:1px
    classDef api fill:#ffd,stroke:#333,stroke-width:1px
    classDef app fill:#fdb,stroke:#333,stroke-width:1px
    classDef ops fill:#ddf,stroke:#333,stroke-width:1px
    
    class INTRA_API,INTRA_CORE intra
    class SPACE_API,SPACE_CORE space
    class TIME_API,TIME_CORE time
    class API_GATEWAY api
    class APP_UI app
    class OPS_CORE ops
```

## Deployment Architecture

The following diagram illustrates the deployment options for GEO-INFER-INTRA:

```mermaid
graph TB
    subgraph "Single-Node Deployment"
        SN_APP[All Components]
        SN_DB[(Database)]
        SN_FS[(File Storage)]
        
        SN_APP --> SN_DB
        SN_APP --> SN_FS
    end
    
    subgraph "Microservices Deployment"
        MS_DOC[Documentation Service]
        MS_KB[Knowledge Base Service]
        MS_ONTO[Ontology Service]
        MS_WF[Workflow Service]
        MS_API[API Gateway]
        
        MS_DOC_DB[(Doc DB)]
        MS_KB_DB[(KB DB)]
        MS_ONTO_DB[(Onto DB)]
        MS_WF_DB[(Workflow DB)]
        MS_FS[(Shared Storage)]
        
        MS_API --> MS_DOC
        MS_API --> MS_KB
        MS_API --> MS_ONTO
        MS_API --> MS_WF
        
        MS_DOC --> MS_DOC_DB
        MS_KB --> MS_KB_DB
        MS_ONTO --> MS_ONTO_DB
        MS_WF --> MS_WF_DB
        
        MS_DOC --> MS_FS
        MS_KB --> MS_FS
        MS_ONTO --> MS_FS
        MS_WF --> MS_FS
    end
    
    subgraph "Containerized Deployment"
        K8S[Kubernetes Cluster]
        HELM[Helm Charts]
        
        K8S --> HELM
    end
    
    subgraph "Serverless Deployment"
        LAMBDA[Lambda Functions]
        S3[S3 Storage]
        DYNAMODB[DynamoDB]
        
        LAMBDA --> S3
        LAMBDA --> DYNAMODB
    end
    
    classDef singleNode fill:#f9f,stroke:#333,stroke-width:1px
    classDef microservices fill:#bbf,stroke:#333,stroke-width:1px
    classDef containerized fill:#dfd,stroke:#333,stroke-width:1px
    classDef serverless fill:#ffd,stroke:#333,stroke-width:1px
    
    class SN_APP,SN_DB,SN_FS singleNode
    class MS_DOC,MS_KB,MS_ONTO,MS_WF,MS_API,MS_DOC_DB,MS_KB_DB,MS_ONTO_DB,MS_WF_DB,MS_FS microservices
    class K8S,HELM containerized
    class LAMBDA,S3,DYNAMODB serverless
```

## Physical Architecture

The following diagram shows a typical physical architecture for a production deployment of GEO-INFER-INTRA:

```mermaid
graph TB
    subgraph "User Access"
        BROWSER[Web Browser]
        MOBILE[Mobile App]
        SCRIPT[Script/API Client]
    end
    
    subgraph "Load Balancer"
        LB[Load Balancer/CDN]
    end
    
    subgraph "Application Servers"
        WEB1[Web Server 1]
        WEB2[Web Server 2]
        API1[API Server 1]
        API2[API Server 2]
    end
    
    subgraph "Service Servers"
        DOC1[Doc Service 1]
        DOC2[Doc Service 2]
        KB1[KB Service 1]
        KB2[KB Service 2]
        ONTO[Ontology Service]
        WF1[Workflow Service 1]
        WF2[Workflow Service 2]
    end
    
    subgraph "Database Servers"
        PRIMARY_DB[(Primary DB)]
        REPLICA_DB[(Replica DB)]
        SEARCH[(Search Engine)]
    end
    
    subgraph "Storage"
        BLOB[(Object Storage)]
        CACHE[(Cache)]
    end
    
    BROWSER --> LB
    MOBILE --> LB
    SCRIPT --> LB
    
    LB --> WEB1
    LB --> WEB2
    LB --> API1
    LB --> API2
    
    WEB1 --> DOC1
    WEB1 --> KB1
    WEB2 --> DOC2
    WEB2 --> KB2
    
    API1 --> ONTO
    API1 --> WF1
    API2 --> ONTO
    API2 --> WF2
    
    DOC1 --> PRIMARY_DB
    DOC2 --> REPLICA_DB
    KB1 --> PRIMARY_DB
    KB2 --> REPLICA_DB
    ONTO --> PRIMARY_DB
    WF1 --> PRIMARY_DB
    WF2 --> REPLICA_DB
    
    DOC1 --> SEARCH
    DOC2 --> SEARCH
    KB1 --> SEARCH
    KB2 --> SEARCH
    
    DOC1 --> BLOB
    DOC2 --> BLOB
    KB1 --> BLOB
    KB2 --> BLOB
    WF1 --> BLOB
    WF2 --> BLOB
    
    DOC1 --> CACHE
    DOC2 --> CACHE
    KB1 --> CACHE
    KB2 --> CACHE
    ONTO --> CACHE
    WF1 --> CACHE
    WF2 --> CACHE
    
    classDef user fill:#fdb,stroke:#333,stroke-width:1px
    classDef loadBalancer fill:#f9f,stroke:#333,stroke-width:1px
    classDef web fill:#bbf,stroke:#333,stroke-width:1px
    classDef service fill:#dfd,stroke:#333,stroke-width:1px
    classDef database fill:#ffd,stroke:#333,stroke-width:1px
    classDef storage fill:#ddf,stroke:#333,stroke-width:1px
    
    class BROWSER,MOBILE,SCRIPT user
    class LB loadBalancer
    class WEB1,WEB2,API1,API2 web
    class DOC1,DOC2,KB1,KB2,ONTO,WF1,WF2 service
    class PRIMARY_DB,REPLICA_DB,SEARCH database
    class BLOB,CACHE storage
```

## Further Information

- [Architecture Overview](overview.md)
- [Data Flow Diagram](data_flow.md)
- [Integration Points](integration_points.md)
- [Deployment Architecture](deployment.md) 