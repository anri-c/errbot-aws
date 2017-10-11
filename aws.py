from errbot import BotPlugin, botcmd, arg_botcmd, webhook
import boto3

class Aws(BotPlugin):
    def _ecs(self):
        client = boto3.client('ecs')

        return client

    def _cf(self):
        client = boto3.client('cloudformation')

        return client

    def _lambda(self):
        client = boto3.client('lambda')

        return client

    def get_configuration_template(self):
        config = {}

        return config

    def activate(self):

        super(Aws, self).activate()

    def deactivate(self):

        super(Aws, self).deactivate()

    def check_configuration(self, configuration):
        """

        """
        super(Aws, self).check_configuration(configuration)

    def callback_connect(self):
        """

        """
        pass

    def callback_message(self, message):
        """

        """
        pass

    def callback_botmessage(self, message):
        """

        """
        pass

    @webhook
    def example_webhook(self, incoming_request):
        """A webhook which simply returns 'Example'"""
        return "Example"

    @botcmd()
    def ecs_clusters(self, message, args):
        """
        get list of ECS clusters
        """
        client = self._ecs()
        response = client.list_clusters()
        clusters = response['clusterArns']

        for cluster in clusters:
            self.send_card(
                title='Ecs Cluster Arn',
                body=cluster,
                in_reply_to=message
            )

    @botcmd()
    def ecs_desc_cluster(self, message, args):
        """
        get ECS cluster desc
        """

        if args is None:
            pass

        else:
            client = self._ecs()
            cluster_list = args.split(',')
            response = client.describe_clusters(clusters=cluster_list)

            for cluster in response['clusters']:
                self.send_card(
                    title=cluster['clusterArn'],
                    fields=(('ClusterName', cluster['clusterName']),
                            ('Status', cluster['status']),
                            ('Instances', cluster['registeredContainerInstancesCount']),
                            ('activeService', cluster['activeServicesCount']),
                            ('runningTask', cluster['runningTasksCount']),
                            ('pendingTask', cluster['pendingTasksCount'])),
                    in_reply_to=message
                )

    @botcmd()
    def ecs_instances(self, message, args):
        """
        """
        if args is None:
            pass
        else:
            client = self._ecs()
            response = client.list_container_instances(cluster=args)
            instance_arns = response['containerInstanceArns']
            instances = client.describe_container_instances(cluster=args, containerInstances=instance_arns)

            for instance in instances['containerInstances']:
                instance_attr = {}
                for attr in instance['attributes']:
                    if 'value' in attr:
                        instance_attr.update({attr['name']: attr['value']})

                self.send_card(
                    title='ClusterInstance',
                    fields=(
                        ('EC2InstanceId', instance['ec2InstanceId']),
                        ('AvailabilityZone', instance_attr['ecs.availability-zone']),
                        ('InstanceType', instance_attr['ecs.instance-type']),
                        ('AmiId', instance_attr['ecs.ami-id']),
                        ('RunningTask', instance['runningTasksCount']),
                        ('Status', instance['status']),
                        ('DockerVersion', instance['versionInfo']['dockerVersion']),
                        ('ECSAgentVersion', instance['versionInfo']['agentVersion'])
                    ),
                    in_reply_to=message
                )

    @botcmd()
    def ecs_services(self, message, args):
        """

        """
        if args is None:
            pass
        else:
            cluster = args
            client = self._ecs()
            response = client.list_services(cluster=cluster)
            service_arns = response['serviceArns']
            services = client.describe_services(cluster=cluster, services=service_arns)

            for service in services['services']:
                self.send_card(
                    title=service['serviceName'],
                    fields=(
                        ('Desired', service['desiredCount']),
                        ('Running', service['runningCount']),
                        ('Pending', service['pendingCount']),
                        ('Status', service['status']),
                        ('taskDefinition', service['taskDefinition'])
                    ),
                    in_reply_to=message
                )

    @botcmd()
    def cf_stacks(self, message, args):
        """
        get list of CloudfoFormation stack
        """
        client = self._cf()
        filter = ['CREATE_IN_PROGRESS','CREATE_COMPLETE',
                'ROLLBACK_IN_PROGRESS','ROLLBACK_FAILED',
                'ROLLBACK_COMPLETE','UPDATE_IN_PROGRESS',
                'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_COMPLETE','UPDATE_ROLLBACK_IN_PROGRESS',
                'UPDATE_ROLLBACK_FAILED',
                'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_ROLLBACK_COMPLETE','REVIEW_IN_PROGRESS']
        response = client.list_stacks(StackStatusFilter=filter)
        stacks = response['StackSummaries']

        for stack in stacks:
            if 'TemplateDescription' not in stack:
                stack['TemplateDescription'] = 'Description is null'

            updated_at = None

            if 'LastUpdatedTime' in stack:
                updated_at = stack['LastUpdatedTime'].isoformat()
            else:
                updated_at = 'No update'

            created_at = stack['CreationTime'].isoformat()

            self.send_card(
                title="CloudFormation" + stack['StackName'] + " Stack status",
                body=stack['TemplateDescription'],
                fields=(
                    ('CreatedAt', created_at),
                    ('UpdatedAt', updated_at),
                    ('Status', stack['StackStatus']),
               ),
                in_reply_to=message
            )
