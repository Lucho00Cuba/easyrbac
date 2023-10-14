# third party's
from pathlib import Path
from yaml import load as yaml_load
from yaml import FullLoader as yaml_FullLoader


class Role(object):
    """roles which are associated to permissions to access resources

    :param name: the name of the role
    """

    roles = {}

    def __init__(self, name=None, description=None):
        """Initializes the a role with the permissions associated with it.

        :param name: <str> object which holds the role name
        :param description: <str> object which holds the role description
        """
        if name != None:
            self.name = name
            self.description = description
            Role.roles[name] = self

    def get_name(self):
        """returns the name of the role
        """
        return self.name

    def __repr__(self):
        return f"<Role {self.name}>"


class User(object):
    """A role gets assigned to a user
    """

    users = {}
    registers = []

    def __init__(self, name=None, roles=[]):
        """Initialises the roles assigned to the user when created or updated later

        :param name: <str>  object which holds the username
        :param roles: <list> object which holds the roles assigned to the user
        """

        if name != None:
            if name not in User.registers:
                self.roles = set(roles)
                self.name = name
                User.users[name] = self
                User.registers.append(name)
            else:
                User.users[name].roles.update(set(roles))

    def add_role(self, role):
        """Adds the role to this user

        :param role: the role to be assigned to the user
        """
        self.roles.add(role)

    def get_roles(self):
        """Returns a generator object for the roles held by the User
        """
        for role in self.roles.copy():
            yield role

    def remove_role(self, role_name):
        """Remove a role assigned to a User

        :param role_name: name of the role which needs to be removed 
        """
        for role in self.get_roles():
            if role.get_name() == role_name:
                self.roles.remove(role)

    def __repr__(self):
        return f"<User {self.name} {self.roles}>"

class RBAC:

    _library = "RBAC"
    _version = "v0.0.1"

    def __init__(self, role=None, user=None, rules=None) -> None:
        """
        Depending on your application's needs, you can provide the Facade with
        existing subsystem objects or force the Facade to create them on its
        own.
        """

        self._role = role or Role()
        self._user = user or User()

        # main
        # load rules defautls
        if rules == None:
            rules = f"{'/'.join(__file__.split('/')[:-2])}/default.yaml"

        try:
            if Path(rules).is_file() is True:
                with open(rules, "r") as f_:
                    data = yaml_load(f_, Loader=yaml_FullLoader)
                    # roles
                    for role in data['rbac']['roles']:
                        Role(role['name'], role['description'])
                        # permissions
                        for item in role['permissions']:
                            for resource in item['resources']:
                                #print(f"Role: {role['name']} Type: {item['method']} Resource: {resource}")
                                self.resource_add_rule(role=self._role.roles[role['name']], method=item['method'], resource=resource)
                    # groups/users
                    for item in data['rbac']['groups']:
                        # getting roles
                        roles = []
                        for role in item['roles']:
                            if role in Role.roles:
                                roles.append(Role.roles[role])
                        # setting user
                        for user in item['users']:
                            User(name=user, roles=roles)
                            # print(f"User: {user} Roles: {roles}")
        except KeyError as err:
            print(f"Failed Rules in {err}")
            exit(1)
        except Exception as err:
            print(f"Failed in {err}")
            exit(1)

        # prints
        #print(f"Load Roles: {Role.roles}")
        #for item in User.users:
        #    print(f"Load User: {User.users[item]}")

    def resource_add_rule(self, role, method, resource):
        """Add rules to allow read access

        :param role: Role of this rule
        :param method: REST verbs allowed to access resource. Include GET, PUT et al.
        :param resource: The resource in question
        """
        try:
            getattr(self, f"_{method}")
        except AttributeError:
            setattr(self, f"_{method}", [])
        finally:
            stream = getattr(self, f"_{method}")

        try:
            #permission = (Role.roles[role].get_name(), method, resource)
            permission = (role.get_name(), method, resource)
        except AttributeError:
            permission = (role, method, resource)
        #except KeyError as err:
        #    print(f"Not found Role: {err}")
        #    exit(1)
        except Exception as err:
            print(f"Err: {err}")
            exit(1)

        if permission not in stream:
            stream.append(permission)

    def is_rule_allowed(self, role, method, resource):
        """returns whether the role is allowed READ access resource
        :return: Boolean
        """

        try:
            getattr(self, f"_{method}")
        except AttributeError:
            setattr(self, f"_{method}", [])
        finally:
            stream = getattr(self, f"_{method}")

        return (role, method, resource) in stream

    def validate(self, username, method, resource):
        state = False
        try:
            for user_role in [role.get_name() for role in self._user.users[username].get_roles()]:
                if self.is_rule_allowed(user_role, method, resource) == True:
                    state = True
                    break
        except KeyError:
            pass
        #print(f"user {username} has privileges to access {resource} : {state}")
        return state
