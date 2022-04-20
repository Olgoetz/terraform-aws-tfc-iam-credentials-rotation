##### GENERAL #####

variable "region" {
  type        = string
  description = "Region to deploy resources to"
  default     = "eu-central-1"
}

variable "default_tags" {
  type        = map(any)
  description = "Default tags to apply to all resources"
  default     = {}
}

#variable "resource_prefix" {
#  type = string
#  description = "Prefix for all resources"
#}



##### TFC #####

variable "tfc_organization_name" {
  type        = string
  description = "Name of the tfc organization"
}

variable "tfc_workspace_name" {
  type        = string
  description = "Name fo the tfc workspace"
}

variable "tfc_workspace_id" {
  type        = string
  description = "ID of the tfc workspace"
}


variable "tfc_token_credential_rotation" {
  type        = string
  description = "API token to authenticate against tfc to enable credential rotation"
  sensitive   = true
}

variable "tfc_url" {
  type        = string
  description = "URL of tfc"
  default     = "https://app.terraform.io"
}

variable "tfc_deployer_user_credential_renewal" {
  type        = number
  description = "Days after when the credentials in tfc have to be renewed"
  default     = 10
}


variable "custom_ca_bundle_path" {
  type        = string
  description = "Path of custom ca bundle for AWS Lambda (must be uploaded with the zip file)"
  default     = null
}

variable "ssl_verify" {
  type        = string
  description = "Activate/Deactivate ssl for lambda updating the credentials in tfc"
  default     = "True"
}


##### CW EVENT ####

variable "tfc_deployer_schedule_expression" {
  type        = string
  description = "Cron expression when to check tfc credentials for validity"
  default     = "cron(0 20 * * ? *)"
}