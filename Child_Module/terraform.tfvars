aws_region = "us-east-1"

vpc_configs = {
  "vpc-059d612141a064cd2": {
    "cidr_block": "10.0.0.0/16",
    "tags": {
      "Name": "project-vpc"
    },
    "enable_dns_support": true,
    "enable_dns_hostnames": true
  }
}

subnet_configs = {
  "subnet-0d32bb791f1c42dfa": {
    "vpc_id": "vpc-059d612141a064cd2",
    "cidr_block": "10.0.128.0/20",
    "availability_zone": "us-east-1a",
    "map_public_ip": false,
    "tags": {
      "Name": "project-subnet-private1-us-east-1a"
    }
  },
  "subnet-0eceb65b434999dbd": {
    "vpc_id": "vpc-059d612141a064cd2",
    "cidr_block": "10.0.0.0/20",
    "availability_zone": "us-east-1a",
    "map_public_ip": false,
    "tags": {
      "Name": "project-subnet-public1-us-east-1a"
    }
  }
}

igw_configs = {
  "igw-050804702a94a3a40": {
    "vpc_id": "vpc-059d612141a064cd2",
    "tags": {
      "Name": "project-igw"
    }
  }
}

nat_configs = {}

sg_configs = {
  "sg-0acfc84c40e502b47": {
    "name": "default",
    "description": "default VPC security group",
    "vpc_id": "vpc-059d612141a064cd2",
    "ingress": [
      {
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": [
          "0.0.0.0/0"
        ]
      }
    ],
    "egress": [
      {
        "from_port": 0,
        "to_port": 0,
        "protocol": "-1",
        "cidr_blocks": [
          "0.0.0.0/0"
        ]
      }
    ],
    "tags": {}
  }
}

rt_configs = {
  "rtb-08825936734f9df96": {
    "vpc_id": "vpc-059d612141a064cd2",
    "routes": [
      {
        "destination_cidr_block": "10.0.0.0/16",
        "gateway_id": "local"
      }
    ],
    "tags": {
      "Name": "project-rtb-private1-us-east-1a"
    }
  },
  "rtb-0c71606b18807d332": {
    "vpc_id": "vpc-059d612141a064cd2",
    "routes": [
      {
        "destination_cidr_block": "10.0.0.0/16",
        "gateway_id": "local"
      }
    ],
    "tags": {}
  },
  "rtb-024acecdd50fb5574": {
    "vpc_id": "vpc-059d612141a064cd2",
    "routes": [
      {
        "destination_cidr_block": "10.0.0.0/16",
        "gateway_id": "local"
      },
      {
        "destination_cidr_block": "0.0.0.0/0",
        "gateway_id": "igw-050804702a94a3a40"
      }
    ],
    "tags": {
      "Name": "project-rtb-public"
    }
  }
}
