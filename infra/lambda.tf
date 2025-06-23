locals {
  lambda_name = "memegen-${var.environment}"

  langsmith_project_name = {
    develop = "MemeGen (Develop)"
    staging = "MemeGen (Staging)"
    main    = "MemeGen (Production)"
  }
}

resource "aws_cloudwatch_log_group" "memegen" {
  name              = "/aws/lambda/${local.lambda_name}"
  retention_in_days = 7
}

resource "aws_lambda_function" "memegen" {
  depends_on = [
    null_resource.ecr_image,
    aws_cloudwatch_log_group.memegen
  ]
  function_name = local.lambda_name
  role          = aws_iam_role.memegen_role.arn
  kms_key_arn   = aws_kms_key.memegen_key.arn
  timeout       = 30
  memory_size   = "2048"
  description   = "MemeGen Lambda"
  image_uri     = "${aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
  publish       = true

  environment {
    variables = {
      APP_ENV                = var.environment
      LOGGER_ENV             = var.environment
      OPENAI_API_KEY         = "mock"
      SERPERDEV_API_KEY      = "mock"
      TAVILY_API_KEY         = "mock"
      LANGSMITH_TRACING      = true
      LANGSMITH_ENDPOINT     = "https://api.smith.langchain.com"
      LANGSMITH_API_KEY      = "mock"
      LANGSMITH_PROJECT      = local.langsmith_project_name[var.environment]
      X_CONSUMER_KEY         = ""
      X_CONSUMER_SECRET      = ""
      X_ACCESS_TOKEN         = ""
      X_ACCESS_TOKEN_SECRET  = ""
      PYTHONWARNINGS         = "ignore::DeprecationWarning"
      TOKENIZERS_PARALLELISM = false
    }
  }
}

resource "aws_lambda_alias" "this" {
  name             = var.environment
  description      = "Alias for MemeGen (${var.environment})"
  function_name    = aws_lambda_function.memegen.function_name
  function_version = aws_lambda_function.memegen.version
}

resource "aws_lambda_permission" "image_post_lambda_events" {
  statement_id  = "AllowExecutionFromEventbridgeScheduler"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.memegen.function_name
  principal     = "scheduler.amazonaws.com"
  qualifier     = aws_lambda_alias.this.name
}

