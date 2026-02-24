variable "bootstrap_servers" {
    description = "Kafka bootstrap servers"
    type = list(string)
    default = ["localhost:9092"]
}
