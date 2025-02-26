# Variables
ENV ?= dev
REGION ?= ap-northeast-2
WORKSPACE ?= $(ENV)
STATE_BUCKET ?= cjhyun-tf-bucket
STATE_KEY ?= $(ENV)/terraform.tfstate
VARS_FILE ?= environments/$(ENV)/terraform.tfvars

# Phony targets
.PHONY: init plan apply destroy fmt validate clean help

# Help target
help:
	@echo "Usage:"
	@echo "  make init ENV=dev        												  - Initialize Terraform for dev environment"
	@echo "  make plan ENV=dev        												  - Plan Terraform changes for dev environment"
	@echo "  make apply ENV=dev       												  - Apply Terraform changes for dev environment"
	@echo "  make destroy ENV=dev     											 	 	- Destroy Terraform resources for dev environment"
	@echo "  make fmt                 												 	- Format Terraform code"
	@echo "  make validate            												  - Validate Terraform code"
	@echo "  make switch-workspace WORKSPACE=<workspace_name>   - Switch Terraform workspace"

# Check if environment is provided
check-env:
	@if [ "$(ENV)" = "" ]; then \
		echo "ENV is not set. Use ENV=<environment>"; \
		exit 1; \
	fi

# Initialize Terraform
init: check-env
	@echo "Initializing Terraform for $(ENV) environment..."
	terraform init \
		-backend=true \
		-backend-config="bucket=$(STATE_BUCKET)" \
		-backend-config="key=$(STATE_KEY)" \
		-backend-config="region=$(REGION)"
	terraform workspace select $(WORKSPACE) || terraform workspace new $(WORKSPACE)

# Plan changes
plan: init
	@echo "Planning Terraform changes for $(ENV) environment..."
	terraform plan \
		-var-file="$(VARS_FILE)" \
		-out=tfplan

# Apply changes
apply: init
	@echo "Applying Terraform changes for $(ENV) environment..."
	terraform apply tfplan

# Destroy resources
destroy: init
	@echo "Destroying Terraform resources for $(ENV) environment..."
	terraform plan -destroy -var-file="$(VARS_FILE)" -out=tfplan
	@echo "Are you sure you want to destroy $(ENV) environment? [y/N]"
	@read -r CONFIRM; \
	if [ "$$CONFIRM" = "y" ]; then \
		terraform apply tfplan; \
	else \
		echo "Destroy cancelled."; \
		exit 1; \
	fi

# Format code
fmt:
	@echo "Formatting Terraform code..."
	terraform fmt -recursive

# Validate code
validate: init
	@echo "Validating Terraform code..."
	terraform validate

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf .terraform/
	rm -f tfplan
	rm -f terraform.tfstate*

# Target for running security checks
security-check:
	@echo "Running security checks..."
	tfsec .
	checkov -d .

# Import existing resources
import: init
	@if [ -z "$(RESOURCE)" ] || [ -z "$(ID)" ]; then \
		echo "Usage: make import RESOURCE=aws_instance.example ID=i-1234567890abcdef0"; \
		exit 1; \
	fi
	terraform import $(RESOURCE) $(ID)

# Show state
show-state: init
	terraform show

# List workspaces
list-workspaces:
	terraform workspace list

# Switch workspace
switch-workspace:
	@if [ -z "$(WORKSPACE)" ]; then \
		echo "Usage: make switch-workspace WORKSPACE=<workspace_name>"; \
		exit 1; \
	fi
	terraform workspace select $(WORKSPACE)