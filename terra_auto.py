import subprocess
import os
import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_vpc_details(vpc_id, region):
    """Fetch VPC details using AWS SDK (Boto3)."""
    ec2_client = boto3.client('ec2', region_name=region)
    try:
        response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        vpc = response['Vpcs'][0]
        cidr_block = vpc['CidrBlock']
        tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
        return cidr_block, tags
    except (ClientError, IndexError) as e:
        logging.error(f"Failed to fetch VPC details: {str(e)}")
        raise
    except NoCredentialsError:
        logging.error("AWS credentials not found.")
        raise

def create_directory_structure(base_path):
    """Create Parent and Child module directories."""
    parent_module = os.path.join(base_path, "Parent_Module")
    child_module = os.path.join(base_path, "Child_Module")
    os.makedirs(parent_module, exist_ok=True)
    os.makedirs(child_module, exist_ok=True)
    return parent_module, child_module

def create_terraform_files(parent_module, child_module):
    """Create Terraform files for Parent and Child modules."""
    parent_main_tf = """
resource "aws_vpc" "my_existing_vpc" {
  for_each = var.imported_vpc_configs
  cidr_block           = each.value.cidr_block
  enable_dns_support   = each.value.enable_dns_support
  enable_dns_hostnames = each.value.enable_dns_hostnames
  tags                 = each.value.tags
}
"""
    parent_variables_tf = """
variable "imported_vpc_configs" {
  description = "Imported VPC configurations"
  type = map(object({
    cidr_block           = string
    enable_dns_support   = bool
    enable_dns_hostnames = bool
    tags                 = map(string)
  }))
  default = {}
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}
"""

    child_main_tf = """
module "imported_vpc" {
  source = "../Parent_Module"
  imported_vpc_configs = var.imported_vpc_configs
  aws_region           = var.aws_region
}
"""
    child_variables_tf = """
variable "imported_vpc_configs" {
  description = "Imported VPC configurations"
  type = map(object({
    cidr_block           = string
    enable_dns_support   = bool
    enable_dns_hostnames = bool
    tags                 = map(string)
  }))
  default = {}
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "existing_vpc_ids" {
  description = "List of existing VPC IDs to import"
  type        = list(string)
  default     = []
}
"""

    backend_tf = """
terraform {
  backend "local" {}
}
"""

    # Write Terraform files
    with open(os.path.join(parent_module, "main.tf"), "w") as f:
        f.write(parent_main_tf)
    with open(os.path.join(parent_module, "variables.tf"), "w") as f:
        f.write(parent_variables_tf)

    with open(os.path.join(child_module, "main.tf"), "w") as f:
        f.write(child_main_tf)
    with open(os.path.join(child_module, "variables.tf"), "w") as f:
        f.write(child_variables_tf)
    with open(os.path.join(child_module, "backend.tf"), "w") as f:
        f.write(backend_tf)

def create_or_update_tfvars(child_module, vpc_id, cidr_block, tags, region):
    """Create or update terraform.tfvars with VPC configurations."""
    formatted_tags = ',\n'.join([f'    {k} = "{v}"' for k, v in tags.items()])
    tfvars_content = f"""
aws_region = "{region}"

existing_vpc_ids = ["{vpc_id}"]

imported_vpc_configs = {{
  "{vpc_id}" = {{
    cidr_block           = "{cidr_block}"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {{
{formatted_tags}
    }}
  }}
}}
"""
    with open(os.path.join(child_module, "terraform.tfvars"), "w") as f:
        f.write(tfvars_content)

def run_command(command, cwd=None):
    """Run a shell command and log output."""
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        logging.error(f"Command failed: {command}")
        logging.error(f"Error: {result.stderr}")
        raise Exception(f"Command {command} failed")
    logging.info(result.stdout)

def main():
    """Main function to automate Terraform process."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    parent_module, child_module = create_directory_structure(base_path)
    create_terraform_files(parent_module, child_module)

    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    vpc_id = "vpc-0d522ed84b46c719d"  # Replace with your VPC ID

    try:
        logging.info(f"Fetching VPC details for {vpc_id}...")
        cidr_block, tags = fetch_vpc_details(vpc_id, region)

        create_or_update_tfvars(child_module, vpc_id, cidr_block, tags, region)

        os.chdir(child_module)
        logging.info("Initializing Terraform...")
        run_command(['terraform', 'init'])

        logging.info(f"Importing VPC {vpc_id}...")
        run_command([
            'terraform', 'import',
            f'module.imported_vpc.aws_vpc.my_existing_vpc["{vpc_id}"]', vpc_id
        ])

        logging.info("Planning Terraform changes...")
        run_command(['terraform', 'plan'])

        logging.info("Applying Terraform changes...")
        run_command(['terraform', 'apply', '-auto-approve'])

        logging.info("VPC import completed successfully.")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
