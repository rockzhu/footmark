"""
Represents an ECS Instance
"""
from footmark.ecs.ecsobject import TaggedECSObject


class Instance(TaggedECSObject):
    """
    Represents an instance.
    """

    def __init__(self, connection=None):
        super(Instance, self).__init__(connection)
        self.tags = {}

    def __repr__(self):
        return 'Instance:%s' % self.id

    def __getattr__(self, name):
        if name == 'id':
            return self.instance_id
        if name == 'name':
            return self.instance_name
        if name == 'state':
            return self.status
        if name in ('inner_ip', 'inner_ip_address'):
            return self.inner_ip_address['ip_address'][0]
        if name in ('public_ip', 'assign_public_ip', 'public_ip_address'):
                return self.public_ip_address['ip_address'][0]
        if name in ('private_ip', 'private_ip_address', 'vpc_private_ip', 'vpc_private_ip_address'):
            return self.vpc_attributes['private_ip_address']['ip_address'][0]
        if name in ('vpc_vswitch_id', 'vswitch_id', 'vpc_subnet_id', 'subnet_id'):
            return self.vpc_attributes['vswitch_id']
        if name == 'vpc_id':
            return self.vpc_attributes['vpc_id']
        if name in ('eip', 'elastic_ip_address'):
            return self.eip_address
        if name in ('group_id', 'security_group_id'):
            return self.security_group_id
        if name in ('group_name', 'security_group_name') and self.security_groups:
            return self.security_groups[0].security_group_name
        if name == 'groups':
            return self.security_groups
        if name in ('key_name', 'keypair', 'key_pair'):
            return getattr(self, 'key_pair_name', '')
        raise AttributeError("Object {0} does not have attribute {1}".format(self.__repr__(), name))

    def __setattr__(self, name, value):
        if name == 'id':
            self.instance_id = value
        if name == 'name':
            self.instance_name = value
        if name == 'status':
            value = value.lower()
        if name == 'state':
            self.status = value
        if name in ('public_ip_address', 'inner_ip_address', 'private_ip_address'):
            if isinstance(value, dict):
                if value['ip_address']:
                    value = value['ip_address'][0]
                else:
                    value = None
        if name  == 'eip_address' and isinstance(value, dict) and value['ip_address']:
            value = value['ip_address']
        if name == 'inner_ip':
            self.inner_ip_address = value
        if name in ('public_ip', 'assign_public_ip'):
            self.public_ip_address = value
        if name in ('private_ip', 'vpc_private_ip', 'vpc_private_ip_address'):
            self.vpc_attributes['private_ip_address'] = value
            self.private_ip_address = value
        if name in ('vpc_vswitch_id', 'vswitch_id', 'vpc_subnet_id', 'subnet_id'):
            self.vpc_attributes['vswitch_id'] = value
        if name == 'vpc_id':
            self.vpc_attributes['vpc_id'] = value
        if name in ('eip', 'elastic_ip_address'):
            self.eip_address = value
        if name in ('group_id', 'security_group_id'):
            if isinstance(value, list) and value:
                value = value[0]
        if name in ('group_name', 'security_group_name') and self.security_groups:
            self.security_groups[0].security_group_name = value
        if name == 'groups':
            self.security_groups = value
        if name in ('key_name', 'keypair', 'key_pair'):
            self.key_pair_name = value
        if name == 'tags' and value:
            v = {}
            for tag in value['tag']:
                if tag.get('tag_key'):
                    v[tag.get('tag_key')] = tag.get('tag_value', None)
            value = v
        super(TaggedECSObject, self).__setattr__(name, value)

    def _update(self, updated):
        self.__dict__.update(updated.__dict__)

    def update(self, validate=False):
        """
        Update the instance's state information by making a call to fetch
        the current instance attributes from the service.

        :type validate: bool
        :param validate: By default, if ECS returns no data about the
                         instance the update method returns quietly.  If
                         the validate param is True, however, it will
                         raise a ValueError exception if no data is
                         returned from ECS.
        """
        rs = self.connection.get_all_instances([self.id])
        if len(rs) > 0:
            for r in rs:
                if r.id == self.id:
                    self._update(r)
        elif validate:
            raise ValueError('%s is not a valid Instance ID' % self.id)
        return self.state

    def start(self):
        """
        Start the instance.
        """
        rs = self.connection.start_instances([self.id])

    def stop(self, force=False):
        """
        Stop the instance

        :type force: bool
        :param force: Forces the instance to stop

        :rtype: list
        :return: A list of the instances stopped
        """
        rs = self.connection.stop_instances([self.id], force)

    def reboot(self, force=False):
        """
        Restart the instance.

        :type force: bool
        :param force: Forces the instance to stop
        """
        return self.connection.reboot_instances([self.id], force)

    def modify(self, name=None, description=None, host_name=None, password=None):
        """
        Modify the instance.

        :type name: str
        :param name: Instance Name
        :type description: str
        :param description: Instance Description
        :type host_name: str
        :param host_name: Instance Host Name
        :type password: str
        :param password: Instance Password
        """
        return self.connection.modify_instances([self.id], name=name, description=description,
                                                host_name=host_name, password=password)

    def terminate(self, force=False):
        """
        Terminate the instance

        :type force: bool
        :param force: Forces the instance to terminate
        """
        rs = self.connection.terminate_instances([self.id], force)

    def join_security_group(self, security_group_id):
        """
        Join one security group

        :type security_group_id: str
        :param security_group_id: The Security Group ID.
        """
        rs = self.connection.join_security_group(self.id, security_group_id)

    def leave_security_group(self, security_group_id):
        """
        Leave one security group

        :type security_group_id: str
        :param security_group_id: The Security Group ID.
        """
        rs = self.connection.leave_security_group(self.id, security_group_id)

    def attach_key_pair(self, key_pair_name):
        """
        Attach one key pair

        :type key_pair_name: str
        :param key_pair_name: The Key Pair Name.
        """
        rs = self.connection.attach_key_pair([self.id], key_pair_name)

    def detach_key_pair(self):
        """
        detach one key pair
        """
        rs = self.connection.detach_key_pair([self.id], self.key_pair_name)
