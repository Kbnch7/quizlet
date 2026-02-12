from prometheus_client import Counter

from .common import registry

courses_created_total = Counter(
    "teaching_courses_created_total",
    "Total number of created courses",
    registry=registry,
)

courses_updated_total = Counter(
    "teaching_courses_updated_total",
    "Total number of updated courses",
    registry=registry,
)

enrollments_created_total = Counter(
    "teaching_enrollments_created_total",
    "Total number of created enrollments",
    registry=registry,
)

enrollments_canceled_total = Counter(
    "teaching_enrollments_canceled_total",
    "Total number of canceled enrollments",
    registry=registry,
)

