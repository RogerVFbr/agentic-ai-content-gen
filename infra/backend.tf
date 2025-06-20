terraform {
  backend "s3" {
    bucket  = "terraform-statefiles-rogervf"
    region  = "us-east-1"
    encrypt = true
  }
}