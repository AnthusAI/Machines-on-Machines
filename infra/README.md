# Machines on Machines infrastructure

`site.json` configures the Papyrus Amplify app-shell stack (the CMS app) for this publication. `package.json` pins `@anthusai/papyrus`, which supplies the template. The Papyrus version is pinned in four places that must agree: `../package.json`, `package.json`, `site.json` (`papyrusVersion`) and `../requirements-publication.txt`.

```bash
npm ci
npx papyrus-infra synth --site site.json
```

Synthesis only prints and writes `cdk.out/`. Deploying is a separate, reviewed step done by a person.

## After the app shell exists

Fill these in, in one change, merge it to `develop`, then release it (the deploy job stays skipped until `app-id` is real):

| Where | Value | Comes from |
| --- | --- | --- |
| `../.github/workflows/deploy.yml` `app-id` | `REPLACE_WITH_CMS_APP_ID` | stack output `CmsAppId` |
| `../.github/workflows/deploy.yml` `role-to-assume` | `arn:aws:iam::712236451410:role/machines-on-machines-github-deploy` | stack output `GithubDeployRoleArn` (confirm it) |
| `../papyrus.config.ts` `publication.edgeDistributionArn` | the edge distribution ARN | the edge stack output `DistributionArn` |
| `../web/projection.json` | add `forms.suggest-edit` and `wiki.suggestForm` | the public form endpoint, once it exists |

## Order

1. Deploy the app shell, then the backend once without `edgeDistributionArn` (first `main` build).
2. Create the edge stack (see the Papyrus `infra/edge/README.md` and Shipped-web's `infra/edge/`) for `machines-on-machines.anth.us`, with `newsroom.machines-on-machines.anth.us` on its own host.
3. Set `edgeDistributionArn` and merge.
4. Point the DNS record at the distribution.
5. Copy the data from read.p.apyr.us with the separate migration tool.

## Edge stack: region-aware cookie notice (`/_papyrus/consent`)

`edge/machines-on-machines.yaml` can answer the Papyrus region-aware cookie notice request at the edge. It is off by default: with `ConsentRegionLookup=false` (the default) the rendered stack is identical to the one before this change (no new resources, no new behavior). With `true` it adds only:

| Resource | What it is |
| --- | --- |
| `ConsentRegionFunction` | CloudFront Function (`cloudfront-js-2.0`, published), the generated Papyrus `infra/edge/consent-region-function.js`. Answers `{"country":"DE","notice":true}` with `cache-control: private, no-store`. Regenerate with Papyrus's `infra/edge/generate_consent_region_function.py` if the region list changes, and paste the code into the template. |
| `ConsentOriginRequestPolicy` | Forwards `CloudFront-Viewer-Country` (only with `ConsentHeaderPolicy=origin-request-policy`, the default). |
| `ConsentCachePolicy` | Puts `CloudFront-Viewer-Country` in the cache key (only with `ConsentHeaderPolicy=cache-policy`). TTL 0/1/1 seconds, because CloudFront refuses cache-key settings when every TTL is 0; the function answers every request itself. |
| one cache behavior | Exact `PathPattern: /_papyrus/consent`, first in `CacheBehaviors`, origin `site-bucket` (never reached), GET and HEAD only, the function on viewer-request, caching disabled (managed CachingDisabled policy with the origin request policy, or the cache policy above). |

AWS documentation does not say whether an origin request policy alone exposes `CloudFront-Viewer-Country` to a viewer-request function. `ConsentHeaderPolicy` lets you switch to `cache-policy` without editing code. Test first in a throwaway stack; do not enable on the live stack before the checks pass. `tests/test_consent_edge.py` and `features/consent-edge.feature` check the template without calling AWS.

### 1. Throwaway test stack (`papyrus-edge-mom-consent-test`)

A separate distribution on its own `cloudfront.net` name (empty `CertificateArn` creates it without aliases). It does not touch the live stack, the live distribution, DNS or the site bucket policy (the consent path never reaches the bucket). Run these as the operator, in `us-east-1`.

Read the live stack's parameters, then write them to a local file that is not committed:

```bash
aws cloudformation describe-stacks --stack-name papyrus-edge-machines-on-machines --region us-east-1 \
  --query 'Stacks[0].Parameters' --output json
```

`consent-test-parameters.json` (copy each value from that output; the placeholders below are not real):

```json
[
  {"ParameterKey": "CertificateArn", "ParameterValue": ""},
  {"ParameterKey": "ApexHost", "ParameterValue": "<ApexHost from the live stack>"},
  {"ParameterKey": "NewsroomHost", "ParameterValue": "<NewsroomHost from the live stack>"},
  {"ParameterKey": "SiteBucketRegionalDomainName", "ParameterValue": "<bucket>.s3.us-east-1.amazonaws.com"},
  {"ParameterKey": "SiteViewerRequestFunctionArn", "ParameterValue": "<SiteViewerRequestFunctionArn from the live stack>"},
  {"ParameterKey": "CmsAppId", "ParameterValue": "<CmsAppId from the live stack>"},
  {"ParameterKey": "ConsentRegionLookup", "ParameterValue": "true"},
  {"ParameterKey": "ConsentHeaderPolicy", "ParameterValue": "origin-request-policy"}
]
```

Create, read and execute the change set:

```bash
aws cloudformation create-change-set --region us-east-1 \
  --stack-name papyrus-edge-mom-consent-test --change-set-name create-1 --change-set-type CREATE \
  --template-body file://infra/edge/machines-on-machines.yaml \
  --parameters file://consent-test-parameters.json --capabilities CAPABILITY_IAM
aws cloudformation wait change-set-create-complete --region us-east-1 \
  --stack-name papyrus-edge-mom-consent-test --change-set-name create-1
aws cloudformation describe-change-set --region us-east-1 \
  --stack-name papyrus-edge-mom-consent-test --change-set-name create-1
aws cloudformation execute-change-set --region us-east-1 \
  --stack-name papyrus-edge-mom-consent-test --change-set-name create-1
aws cloudformation wait stack-create-complete --region us-east-1 --stack-name papyrus-edge-mom-consent-test
aws cloudformation describe-stacks --region us-east-1 --stack-name papyrus-edge-mom-consent-test \
  --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomainName`].OutputValue' --output text
```

Checks (from a US machine, then from a non-US location such as a VPN exit in Germany; `<domain>` is the `DistributionDomainName` output). CloudFront needs a few minutes to deploy the distribution before the first request works.

```bash
curl -sS -D - -o - "https://<domain>/_papyrus/consent"
curl -sS -D - -o - "https://<domain>/_papyrus/consent"   # again: still not a cache hit
```

Pass when, in both places and both requests:

- the status is 200 and the body is `{"country":"<two-letter country of that location>","notice":<bool>}`: the country is non-empty (US gives `"notice":false`; Germany gives `"notice":true`);
- the response has `cache-control: private, no-store`;
- there is no `x-cache: Hit from cloudfront` (`Miss from cloudfront` or `FunctionGeneratedResponse from cloudfront` is expected).

If the country is empty (`{"country":"","notice":true}`) from a place where it should not be, the origin request policy alone does not expose the header to the function. Update the test stack with `ConsentHeaderPolicy=cache-policy` (same commands with `--change-set-type UPDATE`, change-set name `update-1`), read the change set, execute, and repeat the checks. Use whichever passes for production. Also check that a normal page and `/_next/` on the test domain behave as before (the page returns 403 or 404 on the throwaway because the bucket policy trusts only the live distribution; that is expected and not a failure).

Clean up when done:

```bash
aws cloudformation delete-stack --region us-east-1 --stack-name papyrus-edge-mom-consent-test
aws cloudformation wait stack-delete-complete --region us-east-1 --stack-name papyrus-edge-mom-consent-test
```

The not-found Lambda@Edge function replica can take hours to become deletable; if the stack ends in `DELETE_FAILED` on `NotFoundPageFunction`, retry the delete later. The `NotFoundPageVersion` is retained by design.

### 2. Production change set (`papyrus-edge-machines-on-machines`)

Only after step 1 passes, and only when the Papyrus release with `chrome.consent_mode.region_lookup` is ready to ship.

```bash
aws cloudformation create-change-set --region us-east-1 \
  --stack-name papyrus-edge-machines-on-machines --change-set-name consent-lookup-on \
  --template-body file://infra/edge/machines-on-machines.yaml \
  --parameters \
    ParameterKey=CertificateArn,UsePreviousValue=true \
    ParameterKey=ApexHost,UsePreviousValue=true \
    ParameterKey=NewsroomHost,UsePreviousValue=true \
    ParameterKey=SiteBucketRegionalDomainName,UsePreviousValue=true \
    ParameterKey=SiteViewerRequestFunctionArn,UsePreviousValue=true \
    ParameterKey=CmsAppId,UsePreviousValue=true \
    ParameterKey=ConsentRegionLookup,ParameterValue=true \
    ParameterKey=ConsentHeaderPolicy,ParameterValue=<the choice that passed in step 1> \
  --capabilities CAPABILITY_IAM
aws cloudformation wait change-set-create-complete --region us-east-1 \
  --stack-name papyrus-edge-machines-on-machines --change-set-name consent-lookup-on
aws cloudformation describe-change-set --region us-east-1 \
  --stack-name papyrus-edge-machines-on-machines --change-set-name consent-lookup-on
```

Read the change set. It must contain exactly:

- Add `ConsentRegionFunction` (`AWS::CloudFront::Function`);
- Add one policy: `ConsentOriginRequestPolicy` or `ConsentCachePolicy`, matching the choice;
- Modify `SiteDistribution` with `Replacement: False` (an in-place update that adds the `/_papyrus/consent` behavior).

Nothing else may change: no other resource, and above all no `Replacement: True` or `Conditional` replacement of the distribution, the function, the Lambda or the bucket access control. If anything else appears, stop and delete the change set (`aws cloudformation delete-change-set`); do not execute. The owner approves the change set, then:

```bash
aws cloudformation execute-change-set --region us-east-1 \
  --stack-name papyrus-edge-machines-on-machines --change-set-name consent-lookup-on
aws cloudformation wait stack-update-complete --region us-east-1 --stack-name papyrus-edge-machines-on-machines
```

Then run the same two `curl` checks against `https://<ApexHost>/_papyrus/consent` from a US and a non-US location. Only after they pass set `chrome.consent_mode.region_lookup: true` in `web/projection.json` and release the site. Rollback: update the stack with `ConsentRegionLookup=false`; the page script fails closed (the banner shows to everyone) while the address is missing.
