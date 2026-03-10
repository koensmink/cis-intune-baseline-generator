# CIS → Intune Mapping Strategy

## Goal

Translate CIS benchmark controls into Microsoft Intune configuration
policies.

------------------------------------------------------------------------

## Intune configuration mechanisms

  mechanism                  usage
  -------------------------- --------------------------------
  Settings Catalog           standard Windows configuration
  Endpoint Security          Defender, Firewall, BitLocker
  Administrative Templates   legacy GPO policies
  OMA-URI                    CSP configuration fallback

Reference:
https://learn.microsoft.com/en-us/mem/intune/configuration/settings-catalog

------------------------------------------------------------------------

## Mapping priority

1.  Endpoint Security
2.  Settings Catalog
3.  Administrative Templates
4.  Custom OMA-URI
5.  Manual Review

------------------------------------------------------------------------

## Endpoint Security mappings

  category                   Intune policy
  -------------------------- --------------------
  Microsoft Defender         Antivirus policy
  Firewall                   Firewall policy
  BitLocker                  Disk encryption
  Credential Guard           Account protection
  Attack Surface Reduction   ASR rules

Reference:
https://learn.microsoft.com/en-us/mem/intune/protect/endpoint-security

------------------------------------------------------------------------

## Settings Catalog mappings

Example:

CIS Control: 18.9.85.1.1 Turn off Microsoft consumer experiences

Intune Mapping: Settings Catalog → Windows Components → Cloud Content

Value: Enabled

------------------------------------------------------------------------

## Administrative Template mappings

Used when policies originate from ADMX templates such as Edge or Office
configuration.

------------------------------------------------------------------------

## OMA-URI fallback

Example:

./Device/Vendor/MSFT/Policy/Config/CloudContent/DisableWindowsConsumerFeatures

OMA-URI mappings require validation.

------------------------------------------------------------------------

## Confidence scoring

  score   meaning
  ------- ---------------------
  0.95    exact known mapping
  0.75    registry match
  0.50    title pattern
  0.00    manual review

------------------------------------------------------------------------

## Output structure

  field                 description
  --------------------- ---------------------
  cis_id                CIS control
  title                 control title
  implementation_type   Intune mechanism
  intune_area           policy area
  setting_name          Intune setting
  value                 configuration value
  confidence            mapping confidence
