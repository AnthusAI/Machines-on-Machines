import { defineSite } from "@anthusai/papyrus/define-site";
import { machinesOnMachinesBrand } from "./publication/brand";

const defaultCognitoDomainPrefix = "papyrus-machines-on-machines-cms";
const defaultRedirectUrls = [
  "http://localhost:3001/",
  "https://machines-on-machines.anth.us/",
  "https://newsroom.machines-on-machines.anth.us/",
];

function readNonEmptyEnvironmentValue(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

const cognitoDomainPrefixFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_COGNITO_DOMAIN_PREFIX");
const redirectUrlsFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_OAUTH_REDIRECT_URLS");

export const resolvedAuthConfiguration = {
  cognitoDomainPrefix: cognitoDomainPrefixFromEnvironment ?? defaultCognitoDomainPrefix,
  applyCognitoDomainPrefix: readNonEmptyEnvironmentValue("PAPYRUS_APPLY_COGNITO_DOMAIN_PREFIX") !== "false",
  disableGoogleOAuth: readNonEmptyEnvironmentValue("PAPYRUS_DISABLE_GOOGLE_OAUTH") === "1",
  redirectUrls: redirectUrlsFromEnvironment
    ? redirectUrlsFromEnvironment.split(",").map((url) => url.trim()).filter((url) => url.length > 0)
    : defaultRedirectUrls,
};

export default defineSite({
  brands: [machinesOnMachinesBrand],
  defaultBrand: "machines-on-machines",
  backend: {
    brandId: "machines-on-machines",
    auth: resolvedAuthConfiguration,
    publication: {
      kind: "s3-projection",
      staticDir: "web",
      reprojectOnDeploy: true,
      // papyrus-edge-machines-on-machines (infra/edge/machines-on-machines.yaml); lets that distribution read the site bucket.
      edgeDistributionArn: "arn:aws:cloudfront::712236451410:distribution/E1PTZ8B9ZF9GCU",
      // No purge on publish: CloudFront bills every invalidated path after the first 1,000 a month, and curation changes the home page and lists dozens of
      // times a day. Pages are eventually consistent instead: the edge keeps one for five minutes, which still shields the origin from traffic spikes and attacks and keeps the wait to see a change live short. (Ryan, 2026-11-07, shortened from an hour 2026-11-09.)
      cache: { invalidation: "off", htmlSMaxAgeSeconds: 300 },
    },
    stagingBuild: { enabled: false },
    plugins: ["home-page"],
    features: {
      consoleResponder: false,
      inboundEmail: false,
      slack: false,
      storageBackups: false,
    },
  },
});
