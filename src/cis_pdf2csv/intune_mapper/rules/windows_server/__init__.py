from .account_policies import AccountPoliciesRule
from .audit_policy import AuditPolicyRule
from .credential_protection import CredentialProtectionRule
from .defender import DefenderRule
from .event_log import EventLogRule
from .firewall import FirewallRule
from .remote_access import RemoteAccessRule
from .security_options import SecurityOptionsRule

WINDOWS_SERVER_2025_RULES = [
    AccountPoliciesRule(),
    AuditPolicyRule(),
    SecurityOptionsRule(),
    DefenderRule(),
    FirewallRule(),
    CredentialProtectionRule(),
    EventLogRule(),
    RemoteAccessRule(),
]
