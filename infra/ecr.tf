
locals {
  ecr_repository_name = "memegen-repo-${var.environment}"
  ecr_image_tag       = "latest"
  ecr_slim_image_tag  = "slim"
  app_dir             = "../app"
}

resource "aws_ecr_repository" "repo" {
  name = local.ecr_repository_name
}

resource "aws_ecr_lifecycle_policy" "policy" {
  repository = aws_ecr_repository.repo.name
  policy     = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last 1 image(s)",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

data "archive_file" "init" {
  type        = "zip"
  source_dir  = local.app_dir
  output_path = "application_zip_for_hashing.zip"
}

resource "null_resource" "ecr_image" {
  triggers = {
    src_hash = data.archive_file.init.output_sha
  }

  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${local.region}.amazonaws.com
      cd ${local.app_dir}
      echo ""
      echo "+====================+"
      echo "| Building image ... |"
      echo "+====================+"
      echo ""
      docker build -t ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag} .
      # echo "Slim build ..."
      # slim build --show-clogs --show-blogs --http-probe-cmd=GET:/warmup --include-workdir=true --include-path /usr/local --tag ${aws_ecr_repository.repo.repository_url}:${local.ecr_slim_image_tag} ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag}
      # slim xray ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag} .
      # python -m json.tool slim.report.json
      # cat slim.report.json | python -c 'import sys,json;data=json.loads(sys.stdin.read()); print data["test"]'
      # docker image ls
      echo ""
      echo "+====================+"
      echo "| Pushing image ...  |"
      echo "+====================+"
      echo ""
      docker push ${aws_ecr_repository.repo.repository_url}:${local.ecr_image_tag}
      EOF
  }
}

data "aws_ecr_image" "lambda_image" {
  depends_on      = [
    null_resource.ecr_image
  ]
  repository_name = local.ecr_repository_name
  image_tag       = local.ecr_image_tag
}
