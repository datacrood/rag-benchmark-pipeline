CHUNKS: list[str] = [
    # 0 — Auto-scaling and load balancing
    (
        "Cloud infrastructure employs auto-scaling groups to dynamically adjust compute capacity in "
        "response to traffic demand. When CPU utilization exceeds a configured threshold—typically "
        "70%—the orchestrator provisions additional instances within seconds. A load balancer "
        "distributes incoming requests across healthy instances using round-robin or least-connections "
        "algorithms. During peak traffic events, such as product launches or viral content spikes, "
        "the system scales horizontally to prevent any single node from becoming a bottleneck. "
        "Scale-in policies remove excess capacity after sustained low utilization to control costs."
    ),
    # 1 — Node failure and cluster recovery
    (
        "Distributed clusters maintain availability through heartbeat monitoring and automatic "
        "failover mechanisms. Each node broadcasts a heartbeat signal every two seconds; if the "
        "cluster manager detects three consecutive missed heartbeats, it marks the node as "
        "unhealthy and initiates leader election among remaining replicas. Stateful workloads "
        "use persistent volume claims that are reattached to replacement pods within the same "
        "availability zone. Replica sets ensure that a minimum quorum of nodes always holds "
        "a consistent copy of the data, enabling seamless recovery without manual intervention."
    ),
    # 2 — TLS/mTLS for data in transit
    (
        "All data transmitted between services is encrypted using TLS 1.3, which provides "
        "forward secrecy via ephemeral Diffie-Hellman key exchange. For internal service-to-service "
        "communication, mutual TLS (mTLS) is enforced: both the client and server present X.509 "
        "certificates signed by an internal certificate authority. Certificate rotation is automated "
        "via a secrets manager integration that reissues certificates 30 days before expiry. "
        "Terminating TLS at the ingress layer allows plain-text communication within a trusted "
        "private network segment, reducing latency for high-frequency internal calls."
    ),
    # 3 — VPC networking and subnet isolation
    (
        "Network isolation is achieved through Virtual Private Cloud (VPC) architecture with "
        "dedicated subnets segmented by function: public subnets host load balancers and NAT "
        "gateways, while private subnets contain application servers and databases with no "
        "direct internet exposure. Security groups act as stateful firewalls, permitting only "
        "the minimum required ports between tiers. VPC peering enables low-latency communication "
        "between environments without traversing the public internet. Network ACLs provide an "
        "additional stateless filtering layer at the subnet boundary for defense in depth."
    ),
    # 4 — Kubernetes pod scheduling and resource limits
    (
        "Kubernetes schedules pods onto nodes based on resource requests and limits declared in "
        "the pod specification. The scheduler filters nodes that lack sufficient CPU and memory, "
        "then ranks remaining candidates using priority functions weighted toward balanced "
        "resource utilization. Resource limits prevent a single misbehaving pod from consuming "
        "all node resources and causing noisy-neighbor effects. Horizontal Pod Autoscaler (HPA) "
        "monitors custom metrics—such as queue depth or request latency—and adjusts replica "
        "counts automatically. Pod disruption budgets ensure that rolling updates never take "
        "more than a specified percentage of replicas offline simultaneously."
    ),
    # 5 — CDN edge caching and cache invalidation
    (
        "Content Delivery Networks (CDNs) cache static and dynamic assets at geographically "
        "distributed edge nodes to minimize round-trip time for end users. Cache-control headers "
        "dictate TTL values, instructing edge nodes how long to serve stale content before "
        "revalidating with the origin. When a new deployment changes asset hashes, a cache "
        "purge API call propagates invalidation signals to all edge nodes within seconds. "
        "Surrogate keys group related cached objects so that a single invalidation tag can "
        "atomically purge all content associated with a specific entity, such as a user profile "
        "or product listing."
    ),
    # 6 — Database replication and failover
    (
        "Relational databases are deployed in a primary-replica topology with synchronous "
        "replication to at least one standby node within the same region. The primary accepts "
        "all write operations and streams WAL (Write-Ahead Log) records to replicas in real "
        "time. If the primary becomes unreachable, the failover controller promotes the most "
        "up-to-date replica to primary within 30 seconds using a Raft consensus protocol. "
        "Read replicas in additional regions serve geographically distributed read traffic, "
        "reducing latency and offloading the primary. Automated daily snapshots are retained "
        "for 30 days to support point-in-time recovery."
    ),
    # 7 — IAM roles and least-privilege access
    (
        "Identity and Access Management (IAM) enforces least-privilege access by assigning "
        "fine-grained roles to service accounts rather than granting broad permissions. Each "
        "microservice runs under a dedicated service account with only the permissions required "
        "for its specific function—for example, a logging service receives write-only access "
        "to the log sink but cannot read from it. Role bindings are audited weekly against "
        "actual API call patterns, and unused permissions are revoked automatically. Workload "
        "identity federation allows on-premises services to authenticate using short-lived "
        "tokens without storing long-lived credentials."
    ),
    # 8 — CI/CD pipeline and blue-green deployments
    (
        "Continuous integration pipelines execute on every pull request: unit tests, integration "
        "tests, static analysis, and container image scanning must all pass before merge. "
        "Deployments use a blue-green strategy where a new environment (green) is provisioned "
        "in parallel with the current production environment (blue). Traffic is shifted "
        "incrementally using weighted routing rules—10% to green, then 50%, then 100%—with "
        "automated rollback triggered if error rate exceeds a threshold. Canary releases allow "
        "a small subset of real users to validate new features before full promotion. "
        "Deployment history and rollback procedures are stored in a version-controlled runbook."
    ),
    # 9 — Observability: metrics, logs, traces
    (
        "Observability is implemented across three pillars: metrics, structured logs, and "
        "distributed traces. Services emit Prometheus-compatible metrics—request count, "
        "latency histograms, and error rates—scraped every 15 seconds and stored in a "
        "time-series database. Structured JSON logs include a trace ID that correlates "
        "log lines to a specific request across service boundaries. Distributed tracing "
        "using OpenTelemetry propagates span context through HTTP headers, enabling "
        "end-to-end latency attribution. Alerts fire when p99 latency exceeds SLA thresholds "
        "or error budget burn rate crosses predefined limits."
    ),
]
