output "topics" {
    value = {
        learning = kafka_topic.learning_events.name
        course = kafka_topic.course_events.name
        content = kafka_topic.content_events.name
        user = kafka_topic.user_events.name
    }
}
