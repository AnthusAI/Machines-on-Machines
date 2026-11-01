import type { SiteBrand } from "@anthusai/papyrus/lib/site-brand";
import { DEFAULT_THEME_PACK_TOKENS } from "@anthusai/papyrus/lib/site-stack";

export const machinesOnMachinesBrand: SiteBrand = {
  id: "machines-on-machines",
  appTitle: "Machines on Machines",
  appDescription: "Machines on Machines: Information About Information Systems.",
  mastheadTitle: "Machines on Machines",
  mastheadSubtitle: "Information About Information Systems",
  backToHomeLabel: "Back to Machines on Machines",
  articleTitleSuffix: "Machines on Machines",
  placeholderByline: "Machines on Machines",
  defaultPresentation: "blog",
  textFont: '"Archivo", system-ui, sans-serif',
  mastheadWordSplit: false,
  mastheadDateFormat: "formatted",
  mastheadSource: "brand",
  sectionLinkStrategy: "route",
  kanbusTheme: "newspaper-gothic",
  themePack: "papyrus",
  themeTokens: DEFAULT_THEME_PACK_TOKENS,
  renderer: { kind: "markus" },
  hosting: { kind: "amplify-ssr" },
  rootRoute: { kind: "redirect", destination: "/newsroom" },
  newsroomBasePath: "/newsroom",
  opsChrome: "app",
  corpusKey: "machines-on-machines",
  publicationName: "Machines on Machines",
};
