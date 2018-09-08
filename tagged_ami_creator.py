import boto3
import botocore.exceptions as boto_fail
import config_tagged_ami_creator
import time


class TaggedAMICreator:
    def __init__(self):

        # Set up AWS Session + Client + Resources + Waiters
        self.aws_profile = config_tagged_ami_creator.aws_profile
        self.aws_region = config_tagged_ami_creator.aws_region

        # Create custom session
        self.session = boto3.session.Session(profile_name=self.aws_profile, region_name=self.aws_region)

        # Pre-create the clients for reuse
        self.ec2_client = self.session.client("ec2")
        self.ec2_resource = self.session.resource("ec2")

        self.waiter_image_available = self.ec2_client.get_waiter("image_available")
        self.waiter_instance_exists = self.ec2_client.get_waiter("instance_exists")

    def take_image(self, instance_ids):

        report = ""

        for instance_id in instance_ids:

            timestr = time.strftime("%m%d%Y-%H%M")

            # Set the max_attempts for this waiter (default 40)
            self.waiter_instance_exists.config.max_attempts = 1

            try:
                self.waiter_instance_exists.wait(
                    InstanceIds=[
                        instance_id,
                    ]
                )

                instance = self.ec2_resource.Instance(instance_id)
                
            except boto_fail.WaiterError as e:
                if "Max attempts exceeded" in e.message:
                    print("****Instance {} not found in {}. Check configuration.".format(instance_id, self.aws_region))
                    continue
                else:
                    return "ERROR: {} on {}".format(e, instance_id)

            instance_tags = instance.tags
            remove_tags = instance_tags
            instance_name = ""

            for bad_tag in remove_tags:
                if str(bad_tag["Key"]).startswith("aws:"):
                    instance_tags.remove(bad_tag)

            for tag in instance_tags:
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]
                    tag["Value"] = "{}_{}".format(instance_name, timestr)

            # print(instance_tags)

            image = instance.create_image(
                Description="AMI Image for {}".format(instance_name),
                Name="{}_{}".format(instance_name, timestr),
                NoReboot=True
            )

            report += "Created image {} for instance {} named {}.\n".format(image.id, instance.id, instance_name)

            try:
                self.waiter_image_available.wait(
                    ImageIds=[
                        image.id,
                    ]
                )
            except boto_fail.WaiterError as e:
                raise Exception("ERROR: {} waiting for image id {}".format(e, image.id))

            image.create_tags(Tags=instance_tags)

        return report


if __name__ == '__main__':

    my_tagged_ami_creator = TaggedAMICreator()

    print(my_tagged_ami_creator.take_image(config_tagged_ami_creator.instance_ids))
