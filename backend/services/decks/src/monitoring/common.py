from prometheus_client import CollectorRegistry, ProcessCollector

registry = CollectorRegistry()
ProcessCollector(registry=registry)