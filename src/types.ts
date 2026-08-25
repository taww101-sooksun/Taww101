export interface Track {
  id: string;
  title: string;
  artist: string;
  duration: number;
  url: string;
  coverArt?: string;
  bpm?: number;
  key?: string;
  genre?: string;
  isSynthesized?: boolean;
}

export type VisualizerMode = 'bars' | 'wave' | 'circle' | 'dna' | 'matrix';

export interface ThemeConfig {
  id: string;
  name: string;
  accent: string;
  accentGlow: string;
  bgDark: string;
  bgPanel: string;
  borderGlow: string;
}

export interface DjMixerState {
  crossfade: number; // 0 (Deck A) to 1 (Deck B)
  crossfadeCurve: 'linear' | 'constant_power' | 'cut';
  masterVolume: number;
  deckAVolume: number;
  deckBVolume: number;
  deckABpm: number;
  deckBBpm: number;
  deckAPitch: number;
  deckBPitch: number;
  deckALooping: boolean;
  deckBLooping: boolean;
  loopLength: number; // in beats
  filterFrequency: number; // -1 to 1 (lowpass to highpass)
  filterResonance: number;
  reverbMix: number;
  delayMix: number;
  delayTime: number;
  delayFeedback: number;
  distortion: number;
  bassBoost: number;
  stereoPan: number;
  activeDeck: 'A' | 'B';
}

export type CrossfadeCurve = 'linear' | 'constant_power' | 'cut';

export interface EqPreset {
  id: string;
  name: string;
  gains: number[]; // 7 band values in dB (-12 to +12)
}

export type MusicGenreKey = 
  | 'cyber_synthwave'
  | 'neo_pop'
  | 'trap_future'
  | 'acoustic_chill'
  | 'thai_country'
  | 'rock_anthem'
  | 'lofi_midnight'
  | 'edm_festival'
  | 'rnb_soul'
  | 'hyperpop';

export type AutoTuneKey = 'C' | 'C#' | 'D' | 'D#' | 'E' | 'F' | 'F#' | 'G' | 'G#' | 'A' | 'A#' | 'B';
export type AutoTuneScale = 'major' | 'minor' | 'pentatonic' | 'chromatic';

export interface AutoTuneConfig {
  speed: number;
  correctionAmount: number;
  scale: AutoTuneScale;
  key: AutoTuneKey;
  vocalAirEq: number;
  reverbAmount: number;
  delayAmount: number;
  harmoniesGain: number;
  mode: 'subtle_pro' | 'hard_t-pain' | 'alien_vocoder' | 'choir_harmonies';
}

export interface GeneratedSong {
  id: string;
  title: string;
  genre: MusicGenreKey;
  bpm: number;
  duration: number;
  audioUrl: string;
  audioBlob: Blob;
  createdAt: number;
}

export interface PythonApiConfig {
  baseUrl: string;
  isConnected: boolean;
  lastChecked: number | null;
}
