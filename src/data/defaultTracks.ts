import { Track, EqPreset, ThemeConfig } from '../types';

export const DEFAULT_TRACKS: Track[] = [
  {
    id: 'synth-1',
    title: 'Neon Cyber Drive',
    artist: 'Antigravity Studio',
    duration: 145,
    bpm: 126,
    key: 'Fm',
    genre: 'Synthwave',
    url: 'https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=synthwave-80s-110045.mp3',
    coverArt: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=60'
  },
  {
    id: 'synth-2',
    title: 'Future Tokyo Night',
    artist: 'Kavinsky Pulse',
    duration: 180,
    bpm: 128,
    key: 'Am',
    genre: 'Cyberpunk',
    url: 'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=cyberpunk-2099-10701.mp3',
    coverArt: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=60'
  }
];

export const EQ_FREQUENCIES: { freq: number; label: string; type: BiquadFilterType }[] = [
  { freq: 60, label: '60Hz', type: 'lowshelf' },
  { freq: 170, label: '170Hz', type: 'peaking' },
  { freq: 350, label: '350Hz', type: 'peaking' },
  { freq: 1000, label: '1kHz', type: 'peaking' },
  { freq: 3500, label: '3.5kHz', type: 'peaking' },
  { freq: 10000, label: '10kHz', type: 'peaking' },
  { freq: 16000, label: '16kHz', type: 'highshelf' },
];

export const EQ_PRESETS: EqPreset[] = [
  { id: 'flat', name: 'Flat', gains: [0, 0, 0, 0, 0, 0, 0] },
  { id: 'bass', name: 'Bass Boost', gains: [7, 5, 2, 0, 0, 1, 2] },
  { id: 'vocal', name: 'Vocal Enhance', gains: [-2, -1, 1, 4, 5, 3, 1] },
  { id: 'electronic', name: 'Electronic / EDM', gains: [6, 4, -1, -2, 3, 5, 6] },
  { id: 'rock', name: 'Rock Punch', gains: [5, 3, -1, 1, 3, 4, 4] },
];

export const THEME_PRESETS: ThemeConfig[] = [
  {
    id: 'cyber_cyan',
    name: 'Cyber Cyan',
    accent: '#06b6d4',
    accentGlow: '#22d3ee',
    bgDark: '#020617',
    bgPanel: '#0f172a',
    borderGlow: '#0891b2'
  },
  {
    id: 'neon_pink',
    name: 'Neon Magenta',
    accent: '#ec4899',
    accentGlow: '#f472b6',
    bgDark: '#09000d',
    bgPanel: '#1a041f',
    borderGlow: '#db2777'
  }
];

export const SOUND_EFFECTS = [
  { id: 'airhorn', name: '📯 Airhorn', freq: 440, type: 'sawtooth' as OscillatorType },
  { id: 'laser', name: '⚡ Laser Drop', freq: 1200, type: 'sine' as OscillatorType },
  { id: 'subdrop', name: '💣 808 Sub Drop', freq: 80, type: 'sine' as OscillatorType },
  { id: 'rewind', name: '⏪ Scratch Rewind', freq: 600, type: 'triangle' as OscillatorType },
];
