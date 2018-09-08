#!/usr/bin/python

# AWS profile you are referencing for authentication.  If you don't have a profile set to "default"
# aws_profile = "default"
aws_profile = "firstwatch"

# AWS region you want to run in.
aws_region = "us-east-1"  # for local testing
# aws_region = "us-east-1"

# Comma delimited array of quoted instance ids to create AMIs for.
instance_ids = ["i-076e8f0c1272e75ba", "i-038d6442ff191c2a8"]
