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
