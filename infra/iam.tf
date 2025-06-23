
locals{
  bucket = "memegen-persistence-${var.environment}"
}

resource "aws_iam_role" "memegen_role" {
  name               = "RoleforMemeGenLambda-${var.environment}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "memegen_lambda_logging_${var.environment}"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.memegen_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_policy" "lambda_s3" {
  name        = "memegen_lambda_s3_${var.environment}"
  path        = "/"
  description = "IAM policy for reading/writing to S3 from a lambda"

  policy = <<EOF
  {
   "Version": "2012-10-17",
   "Statement": [
       {
           "Sid": "ListObjectsInBucket",
           "Effect": "Allow",
           "Action": "s3:ListBucket",
           "Resource": "arn:aws:s3:::${local.bucket}"
       },
       {
           "Sid": "AllObjectActions",
           "Effect": "Allow",
           "Action": "s3:*Object",
           "Resource": "arn:aws:s3:::${local.bucket}/*"
       }
   ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.memegen_role.name
  policy_arn = aws_iam_policy.lambda_s3.arn
}

resource "aws_iam_policy" "lambda_parameter_store" {
  name        = "memegen_lambda_parameter_store_${var.environment}"
  path        = "/"
  description = "IAM policy for reading from Parameter Store from a lambda"
  policy      = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowGetParameter",
            "Effect": "Allow",
            "Action": "ssm:GetParameter",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "parameter_store" {
  role       = aws_iam_role.memegen_role.name
  policy_arn = aws_iam_policy.lambda_parameter_store.arn
}
