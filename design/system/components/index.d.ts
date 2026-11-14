import type * as React from 'react';

export type Role = 'brand' | 'machine' | 'human';

export interface WordmarkProps { layout?: 'inline' | 'stacked' | 'vertical'; subject?: string; size?: string | number; as?: string; className?: string }
export declare function Wordmark(props: WordmarkProps): React.ReactElement;

export interface StickerProps { subject?: string; tagline?: string; taglineVariant?: 'display' | 'text'; headingLevel?: 1 | 2 | 3; flat?: boolean; className?: string; children?: React.ReactNode }
export declare function Sticker(props: StickerProps): React.ReactElement;

export interface SpineProps { subject?: string; progress?: number; showProgress?: boolean; homeHref?: string; sectionHref?: string; className?: string }
export declare function Spine(props: SpineProps): React.ReactElement;

export interface LoopBandProps { role?: Role; words?: string[]; repeat?: number; offset?: number; label?: string; className?: string }
export declare function LoopBand(props: LoopBandProps): React.ReactElement;

export type PlaceholderComposition = 'sun-slab' | 'rising' | 'eclipse' | 'moon' | 'horizon' | 'pages';
export type PlaceholderKind = 'paper';
export interface PlaceholderArtProps { seed?: string; kind?: PlaceholderKind; composition?: PlaceholderComposition; tone?: Role; className?: string }
export declare function PlaceholderArt(props: PlaceholderArtProps): React.ReactElement;
export declare function choosePlaceholderArt(seed: string, kind?: PlaceholderKind): { composition: PlaceholderComposition; tone: Role };

export interface ProvenanceEntry { role: Role; label: string }

export interface StoryCardProps { headline: string; blurb?: string; kicker?: string; meta?: string; provenance?: ProvenanceEntry[]; image?: string; imageAlt?: string; imageTone?: Role; imageSeed?: string; size?: 'large' | 'small'; href?: string; className?: string }
export declare function StoryCard(props: StoryCardProps): React.ReactElement;

export interface ReferenceCardProps { title: string; summary?: string; stars?: 1 | 2 | 3 | 4 | 5; status: 'accepted' | 'recommended'; actor?: 'human' | 'cyclotron' | 'agent' | 'rule'; confidence?: number; siteName?: string; host?: string; age?: string; image?: string; imageTone?: Role; imageSeed?: string; kind?: PlaceholderKind; href?: string; className?: string }
export declare function ReferenceCard(props: ReferenceCardProps): React.ReactElement;

export interface ThreadCardProps { title: string; anchor?: string; author?: string; latest?: string; messages?: number; lastAt?: string; image?: string; imageTone?: Role; imageSeed?: string; href?: string; className?: string }
export declare function ThreadCard(props: ThreadCardProps): React.ReactElement;

export interface ProposalRowProps { title: string; net?: number; state?: string; approved?: boolean; href?: string; onVoteUp?: React.MouseEventHandler; onVoteDown?: React.MouseEventHandler; className?: string }
export declare function ProposalRow(props: ProposalRowProps): React.ReactElement;

export interface ProvenanceChipProps { role?: Role; className?: string; children?: React.ReactNode }
export declare function ProvenanceChip(props: ProvenanceChipProps): React.ReactElement;

export interface ButtonProps { variant?: 'human' | 'brand' | 'quiet'; href?: string; type?: 'button' | 'submit'; onClick?: React.MouseEventHandler; className?: string; children?: React.ReactNode }
export declare function Button(props: ButtonProps): React.ReactElement;

export interface NavPillProps { active?: boolean; href?: string; className?: string; children?: React.ReactNode }
export declare function NavPill(props: NavPillProps): React.ReactElement;

export interface LanguageAlternate { tag: string; name: string; url: string }
export interface LanguageSwitcherProps { alternates: LanguageAlternate[]; current: string; label?: string; open?: boolean; className?: string }
export declare function LanguageSwitcher(props: LanguageSwitcherProps): React.ReactElement;

export interface LanguageBannerProps { mode?: 'offer' | 'read' | 'note'; lang?: string; strings: Record<string, string>; seconds?: number; href?: string; className?: string }
export declare function LanguageBanner(props: LanguageBannerProps): React.ReactElement;

export interface WireCardProps { section?: string; title: string; source?: string; score?: number; href?: string; className?: string }
export declare function WireCard(props: WireCardProps): React.ReactElement;

export interface WikiCardProps { term: string; definition?: string; relation?: string; href?: string; className?: string }
export declare function WikiCard(props: WikiCardProps): React.ReactElement;

export interface PullQuoteProps { className?: string; children?: React.ReactNode }
export declare function PullQuote(props: PullQuoteProps): React.ReactElement;

declare global {
  interface Window {
    MoM: {
      Wordmark: typeof Wordmark; Sticker: typeof Sticker; Spine: typeof Spine; LoopBand: typeof LoopBand;
      StoryCard: typeof StoryCard; ReferenceCard: typeof ReferenceCard; ThreadCard: typeof ThreadCard; ProposalRow: typeof ProposalRow;
      ProvenanceChip: typeof ProvenanceChip; Button: typeof Button; NavPill: typeof NavPill; LanguageSwitcher: typeof LanguageSwitcher; LanguageBanner: typeof LanguageBanner;
      WireCard: typeof WireCard; WikiCard: typeof WikiCard; PullQuote: typeof PullQuote;
    };
  }
}
