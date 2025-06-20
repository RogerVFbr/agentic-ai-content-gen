resource "aws_kms_key" "memegen_key" {
  description = "FIAP Api KMS Key."
  deletion_window_in_days = 7
  enable_key_rotation = true
  policy = ""
}

resource "aws_kms_alias" "memegen_key" {
  name = "alias/fiap-api-cmk-${var.environment}"
  target_key_id = aws_kms_key.memegen_key.key_id
}

data "aws_iam_policy_document" "memegen_key" {
  statement {
    sid = "Allow administration of the key."
    effect = "Allow"

    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }

    actions = ["kms:"]

    resources = ["*"]

    condition {
      test     = "ForAnyValue:StringEquals"
      values   = [data.aws_caller_identity.current.account_id]
      variable = "kms:CallerAccount"
    }
  }

  statement {
    sid = "Allow use of the key."
    effect = "Allow"

    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey"
    ]

    resources = ["*"]
  }

  statement {
    sid = "Allow attachmente of persistent resources."
    effect = "Allow"

    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }

    resources = ["*"]

    condition {
      test     = "Bool"
      values   = ["true"]
      variable = "kms:GrantIsForAwsResource"
    }
  }

  statement {
    sid = "Allow Lambda to use key."
    effect = "Allow"

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }

    actions = [
      "kms:GenerateDataKey",
      "kms:Decrypt"
    ]

    resources = ["*"]
  }
}
