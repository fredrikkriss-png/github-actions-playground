terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.6.0"
    }
  }
}

provider "random" {}

resource "random_pet" "my_pet" {
  length = 2
}

output "pet_name" {
  value = random_pet.my_pet.id
}
