# -----------------------------------------------------------------------------------------------------
# PROVIDER, DATA SOURCES, LOCALS
# -----------------------------------------------------------------------------------------------------

provider "aws" {
  region = var.region
  default_tags {
    tags = var.default_tags
  }
}


data "aws_caller_identity" "this" {}
data "aws_region" "this" {}

locals {
  tfc_deployer         = "${var.tfc_organization_name}-${var.tfc_workspace_name}-deployer"
  lambda_function_name = "${var.tfc_organization_name}-${var.tfc_workspace_name}-credentials-rotator"
}

# -----------------------------------------------------------------------------------------------------
# LAMBDA
# Lambda to rotate tfc credentials
# -----------------------------------------------------------------------------------------------------




data "archive_file" "tfc_deployer_lambda" {
  output_path = "./lambda_payload.zip"
  source_dir  = "${path.module}/lambda_function"
  type        = "zip"
}

#tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "tfc_deployer_lambda" {
  function_name    = local.lambda_function_name
  role             = aws_iam_role.tfc_deployer_lambda_role.arn
  description      = "Rotates the IAM credentials for TFC workspace '${var.tfc_workspace_name}' in TFC organization '${var.tfc_organization_name}'."
  filename         = data.archive_file.tfc_deployer_lambda.output_path
  source_code_hash = data.archive_file.tfc_deployer_lambda.output_base64sha256
  runtime          = "python3.8"
  handler          = "handler.lambda_handler"
  timeout          = "300"

  environment {
    variables = {

      TFC_TOKEN             = var.tfc_token_credential_rotation
      TFC_ORG               = var.tfc_organization_name
      TFC_URL               = var.tfc_url
      TFC_WORKSPACE_ID      = var.tfc_workspace_id
      TFC_DEPLOYER_NAME     = local.tfc_deployer
      SSL_VERIFY            = var.ssl_verify
      FORCE_CREATE_NEW_KEY  = "False"
      LOG_LEVEL             = "INFO"
      RENEWAL_TIME          = var.tfc_deployer_user_credential_renewal
      CUSTOM_CA_BUNDLE_PATH = var.custom_ca_bundle_path
    }
  }
}

resource "aws_iam_role" "tfc_deployer_lambda_role" {
  name        = local.lambda_function_name
  description = "Lambda role for ${local.lambda_function_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  inline_policy {
    name   = "${local.lambda_function_name}-lambda-policy"
    policy = data.aws_iam_policy_document.tfc_deployer_lambda_policy_inline.json
  }
}

data "aws_iam_policy_document" "tfc_deployer_lambda_policy_inline" {
  statement {
    effect = "Allow"
    actions = ["logs:CreateLogGroup",
      "logs:CreateLogStream",
    "logs:PutLogEvents"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = ["iam:CreateUser",
      "iam:CreateAccessKey",
      "iam:DeleteAccessKey",
    "iam:ListAccessKeys"]
    resources = ["arn:aws:iam::${data.aws_caller_identity.this.account_id}:user/${local.tfc_deployer}"]
  }
  statement {
    effect    = "Allow"
    actions   = ["iam:ListUsers"]
    resources = ["arn:aws:iam::${data.aws_caller_identity.this.account_id}:*"]
  }
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "tfc_deployer_lambda_log_group" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 3
  depends_on        = [aws_lambda_function.tfc_deployer_lambda]
}

data "aws_lambda_invocation" "tfc_deployer_lambda_invocation" {
  depends_on    = [aws_lambda_function.tfc_deployer_lambda]
  function_name = local.lambda_function_name
  input         = jsonencode({ "Message" : "Executed from Terraform" })
}

# -----------------------------------------------------------------------------------------------------
# IAM
# IAM user for tfc
# -----------------------------------------------------------------------------------------------------

resource "aws_iam_user" "tfc_deployer_user" {
  name = local.tfc_deployer
}

data "aws_iam_policy" "tfc_deployer_user_policy" {
  name = aws_iam_user.tfc_deployer_user.name
}

resource "aws_iam_user_policy_attachment" "tfc_deployer_user_policy" {
  policy_arn = data.aws_iam_policy.tfc_deployer_user_policy.arn
  user       = aws_iam_user.tfc_deployer_user.name
}


# -----------------------------------------------------------------------------------------------------
# CLOUDWATCH
# CloudWatch event to schedule rotation of credentials
# -----------------------------------------------------------------------------------------------------

resource "aws_lambda_permission" "tfc_deployer_lambda_permissions" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tfc_deployer_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tfc_deployer_cw_event_rule.arn
}

resource "aws_cloudwatch_event_rule" "tfc_deployer_cw_event_rule" {
  name                = "${local.tfc_deployer}-cw-event-rule"
  description         = "Rule to check validity of ${aws_iam_user.tfc_deployer_user.name}"
  schedule_expression = var.tfc_deployer_schedule_expression
}

resource "aws_cloudwatch_event_target" "tfc_deployer_cw_event_target" {
  target_id = aws_lambda_function.tfc_deployer_lambda.function_name
  arn       = aws_lambda_function.tfc_deployer_lambda.arn
  rule      = aws_cloudwatch_event_rule.tfc_deployer_cw_event_rule.name
}
