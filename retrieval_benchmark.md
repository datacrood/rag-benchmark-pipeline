# Retrieval Benchmark: Strategy A vs Strategy B

**Corpus:** 10 cloud infrastructure technical paragraphs  
**Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)  
**Similarity metric:** Cosine similarity (L2-normalize + dot product)  
**Strategy A:** Raw embedding of original query  
**Strategy B:** Template-expanded query before embedding  

---

## Query: *How does the system handle peak load?*

**Strategy B expanded query:**  
`How does the system handle peak load? peak load traffic spike high concurrency auto-scaling load balancer burst capacity horizontal scaling throughput`

| Strategy   |   Rank |   Score | Chunk (first 120 chars)                                                                                                  |
|------------|--------|---------|--------------------------------------------------------------------------------------------------------------------------|
| A          |      1 |  0.5072 | Cloud infrastructure employs auto-scaling groups to dynamically adjust compute capacity in response to traffic demand. W |
| A          |      2 |  0.3598 | Kubernetes schedules pods onto nodes based on resource requests and limits declared in the pod specification. The schedu |
| A          |      3 |  0.3199 | Relational databases are deployed in a primary-replica topology with synchronous replication to at least one standby nod |
| B          |      1 |  0.7135 | Cloud infrastructure employs auto-scaling groups to dynamically adjust compute capacity in response to traffic demand. W |
| B          |      2 |  0.4818 | Kubernetes schedules pods onto nodes based on resource requests and limits declared in the pod specification. The schedu |
| B          |      3 |  0.4237 | Relational databases are deployed in a primary-replica topology with synchronous replication to at least one standby nod |


**Overlap:** 3/3 chunks shared between strategies

---

## Query: *What happens when a node fails in the cluster?*

**Strategy B expanded query:**  
`What happens when a node fails in the cluster? node failure cluster recovery heartbeat leader election replica failover availability zone pod restart`

| Strategy   |   Rank |   Score | Chunk (first 120 chars)                                                                                                  |
|------------|--------|---------|--------------------------------------------------------------------------------------------------------------------------|
| A          |      1 |  0.5866 | Distributed clusters maintain availability through heartbeat monitoring and automatic failover mechanisms. Each node bro |
| A          |      2 |  0.4111 | Relational databases are deployed in a primary-replica topology with synchronous replication to at least one standby nod |
| A          |      3 |  0.3293 | Kubernetes schedules pods onto nodes based on resource requests and limits declared in the pod specification. The schedu |
| B          |      1 |  0.7246 | Distributed clusters maintain availability through heartbeat monitoring and automatic failover mechanisms. Each node bro |
| B          |      2 |  0.4496 | Kubernetes schedules pods onto nodes based on resource requests and limits declared in the pod specification. The schedu |
| B          |      3 |  0.4304 | Relational databases are deployed in a primary-replica topology with synchronous replication to at least one standby nod |


**Overlap:** 3/3 chunks shared between strategies

---

## Query: *How is data secured during transmission?*

**Strategy B expanded query:**  
`How is data secured during transmission? data security TLS mTLS encryption in transit certificate PKI forward secrecy mutual authentication`

| Strategy   |   Rank |   Score | Chunk (first 120 chars)                                                                                                  |
|------------|--------|---------|--------------------------------------------------------------------------------------------------------------------------|
| A          |      1 |  0.4178 | All data transmitted between services is encrypted using TLS 1.3, which provides forward secrecy via ephemeral Diffie-He |
| A          |      2 |  0.246  | Observability is implemented across three pillars: metrics, structured logs, and distributed traces. Services emit Prome |
| A          |      3 |  0.2414 | Network isolation is achieved through Virtual Private Cloud (VPC) architecture with dedicated subnets segmented by funct |
| B          |      1 |  0.6419 | All data transmitted between services is encrypted using TLS 1.3, which provides forward secrecy via ephemeral Diffie-He |
| B          |      2 |  0.2016 | Network isolation is achieved through Virtual Private Cloud (VPC) architecture with dedicated subnets segmented by funct |
| B          |      3 |  0.1822 | Content Delivery Networks (CDNs) cache static and dynamic assets at geographically distributed edge nodes to minimize ro |


**Overlap:** 2/3 chunks shared between strategies

**Only in Strategy B (new retrievals from expansion):**
- _Content Delivery Networks (CDNs) cache static and dynamic assets at geographically distributed edge ..._

**Only in Strategy A (lost after expansion):**
- _Observability is implemented across three pillars: metrics, structured logs, and distributed traces...._

---
