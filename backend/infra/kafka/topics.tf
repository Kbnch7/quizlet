resource "kafka_topic" "learning_events" {
    name = "learning.events"
    partitions = 6
    replication_factor = 1
    
    config = {
        "cleanup.policy" = "delete"
        "retention.ms" = "1209600000" # 14 days
        "segment.ms" = "3600000"
    }
}

resource "kafka_topic" "course_events" {
    name = "course.events"
    partitions = 3
    replication_factor = 1
    
    config = {
        "cleanup.policy" = "delete"
        "retention.ms" = "2592000000" # 30 days
    }
}

resource "kafka_topic" "content_events" {
    name = "content.events"
    partitions = 3
    replication_factor = 1

    config = {
        "cleanup.policy" = "compact"
        "min.cleanable.dirty.ratio" = "0.1"
    }
}

resource "kafka_topic" "user_events" {
    name = "user.events"
    partitions = 2
    replication_factor = 1

    config = {
        "cleanup.policy" = "compact"
    }
}

