output "tfc_deployer_user_arn" {
  value       = aws_iam_user.tfc_deployer_user.arn
  description = "ARN of the tfc deployer user"
}

output "tfc_deployer_lambda_function_arn" {
  value       = aws_lambda_function.tfc_deployer_lambda.arn
  description = "ARN of the lambda function that sets credentials in tfc"
}

