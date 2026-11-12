import { defineSite } from "@anthusai/papyrus/define-site";
import { machinesOnMachinesBrand } from "./publication/brand";
import sectionList from "./web/sections.json";

// The forum: the site-wide conversations page, its thread pages, and each section's conversations page. The edge keeps these for seconds, not minutes, so a reply shows up while people are still talking.
const liveForumPrefixes = ["conversations/", ...sectionList.sections.map((section) => `${section.id}/conversations/`)];

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
      cache: { invalidation: "off", htmlSMaxAgeSeconds: 300, livePrefixes: liveForumPrefixes },
    },
    stagingBuild: { enabled: false },
    plugins: [
      "home-page",
      {
        name: "notifications",
        siteId: "machines-on-machines",
        siteOrigin: "https://machines-on-machines.anth.us",
        basePath: "",
        // The compute role of this site's CMS app (the CmsComputeRoleArn output of amplify-app-shell-machines-on-machines-cms).
        computeRoleArn: "arn:aws:iam::712236451410:role/amplify-app-shell-machine-AmplifyComputeRoleD988057-9M21hBacB13d",
        sendingDomain: "mail.machines-on-machines.anth.us",
        fromAddress: "notifications@mail.machines-on-machines.anth.us",
        fromName: "Machines on Machines",
        theme: { accent: "#e2725f", text: "#111111", background: "#ffffff" },
        lists: [{ id: "stories", name: "New articles and posts", rule: { types: ["article", "post"] }, approval: "admin" }],
      },
    ],
    features: {
      consoleResponder: false,
      inboundEmail: false,
      slack: false,
      storageBackups: false,
    },
  },
});
