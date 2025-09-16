terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "2.5.1"
    }
  }
}

provider "local" {}

resource "local_file" "hello" {
  content  = "Hello from Terraform via GitHub Actions!"
  filename = "${path.module}/hello.txt"
}
