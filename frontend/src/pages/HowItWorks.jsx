import React from 'react';
import { 
  BookOpen, 
  Binary, 
  ShieldAlert, 
  Layers, 
  Cpu, 
  Lock, 
  Music, 
  Video, 
  CheckCircle2, 
  EyeOff, 
  Key,
  ShieldCheck,
  FileCode
} from 'lucide-react';

export default function HowItWorks() {
  return (
    <div className="space-y-10 max-w-5xl mx-auto animate-fade-in pb-16">
      {/* Page Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
          <BookOpen className="w-5 h-5" />
          <span className="text-xs font-mono font-semibold tracking-wider uppercase">Cybersecurity Educational Blueprint</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">How Media Steganography Works</h2>
        <p className="text-sm text-slate-300 mt-2 max-w-3xl leading-relaxed">
          A technical guide to digital steganography, least significant bit (LSB) carrier modulation, 
          lossless video reassembly, and defense-in-depth authenticated encryption.
        </p>
      </div>

      {/* 1. Steganography vs Cryptography */}
      <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/50 flex items-center justify-center text-cyan-400">
            <EyeOff className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">1. Steganography vs. Cryptography</h3>
            <p className="text-xs text-slate-400 font-mono">Concealment of Existence vs. Scrambling of Content</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
            <div className="text-sm font-bold text-cyan-400 flex items-center gap-2">
              <EyeOff className="w-4 h-4" />
              Steganography (Covert Communication)
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Derived from Greek <em>steganos</em> ("hidden") and <em>graphein</em> ("writing"). The objective is to 
              <strong> hide the very existence of a communication channel</strong>. An interceptor examining the media 
              perceives only an ordinary audio track or video clip without suspecting an embedded payload.
            </p>
            <div className="text-[11px] font-mono text-cyan-300 bg-cyan-950/40 p-2.5 rounded-lg border border-cyan-800/30">
              Goal: Unobservability & Plausible Deniability
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
            <div className="text-sm font-bold text-purple-400 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Cryptography (Confidentiality)
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Transforms plaintext into ciphertext using mathematical keys. While an adversary cannot decrypt the message 
              without the key, <strong>the existence of the secret communication is immediately obvious</strong>, 
              which can trigger suspicion or censorship in high-threat environments.
            </p>
            <div className="text-[11px] font-mono text-purple-300 bg-purple-950/40 p-2.5 rounded-lg border border-purple-800/30">
              Goal: Secrecy & Authenticity of Content
            </div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-950/40 via-purple-950/40 to-slate-950/60 border border-slate-800 text-xs text-slate-300">
          <strong className="text-white">Our Hybrid Architecture:</strong> We combine both! The secret payload is first 
          encrypted using authenticated AES-256-GCM. Then, the resulting ciphertext is embedded into media via LSB. 
          Even if an adversary suspects steganography, they cannot decrypt the payload or forge modifications.
        </div>
      </div>

      {/* 2. LSB Algorithm Visual Diagram */}
      <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-950/80 border border-purple-800/50 flex items-center justify-center text-purple-400">
            <Binary className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">2. The Least Significant Bit (LSB) Technique</h3>
            <p className="text-xs text-slate-400 font-mono">Modulating the lowest energy bits of carrier data</p>
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Digital media represents sound waves and video pixels as binary numbers. In a 16-bit audio sample or 8-bit RGB color byte, 
          the <strong>Most Significant Bits (MSBs)</strong> carry coarse visual/acoustic information, whereas the 
          <strong>Least Significant Bit (LSB)</strong> represents minimal perceptible energy.
        </p>

        {/* Visual Byte Substitution Table */}
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-4 font-mono text-xs">
          <div className="text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
            Example: Embedding secret bit '1' into an audio sample
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <span className="text-slate-400 block text-[10px]">ORIGINAL 16-BIT SAMPLE</span>
              <div className="text-sm font-bold text-slate-100">14,208 (0x3780)</div>
              <div className="text-slate-400 text-[11px] tracking-widest">
                0011 0111 1000 000<span className="text-cyan-400 font-bold underline">0</span>
              </div>
              <span className="text-[10px] text-slate-500 block">Original LSB = 0</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-purple-800/40 space-y-2">
              <span className="text-purple-400 block text-[10px]">SECRET PAYLOAD BIT</span>
              <div className="text-sm font-bold text-purple-300">Target Bit: 1</div>
              <div className="text-purple-400 text-[11px]">Bitwise: (sample & ~1) | 1</div>
              <span className="text-[10px] text-slate-500 block">Replaces LSB with 1</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-800/40 space-y-2">
              <span className="text-emerald-400 block text-[10px]">STEGO 16-BIT SAMPLE</span>
              <div className="text-sm font-bold text-emerald-300">14,209 (0x3781)</div>
              <div className="text-slate-300 text-[11px] tracking-widest">
                0011 0111 1000 000<span className="text-emerald-400 font-bold underline">1</span>
              </div>
              <span className="text-[10px] text-emerald-400/80 block">Delta = +0.0015% (Audibly Zero)</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Binary Envelope Protocol */}
      <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
            <FileCode className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">3. Self-Describing Binary Envelope Protocol</h3>
            <p className="text-xs text-slate-400 font-mono">Structured metadata format with integrity validation</p>
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Many primitive steganography implementations rely on external assumptions or hardcoded length delimiters. 
          Our system serializes data into a strict 18-byte binary envelope before embedding:
        </p>

        {/* Binary Protocol Spec Diagram */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 font-mono text-center">
          <div className="p-3 rounded-xl bg-slate-950 border border-cyan-800/60">
            <span className="text-[10px] text-slate-500 block">4 BYTES</span>
            <span className="text-xs font-bold text-cyan-300">MAGIC</span>
            <span className="text-[9px] text-slate-400 block mt-1">b'STEG'</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[10px] text-slate-500 block">1 BYTE</span>
            <span className="text-xs font-bold text-slate-200">VERSION</span>
            <span className="text-[9px] text-slate-400 block mt-1">0x01</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[10px] text-slate-500 block">1 BYTE</span>
            <span className="text-xs font-bold text-purple-300">FLAGS</span>
            <span className="text-[9px] text-slate-400 block mt-1">ENC / FILE</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-emerald-800/60">
            <span className="text-[10px] text-slate-500 block">4 BYTES</span>
            <span className="text-xs font-bold text-emerald-300">CRC32</span>
            <span className="text-[9px] text-slate-400 block mt-1">Integrity</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[10px] text-slate-500 block">2 BYTES</span>
            <span className="text-xs font-bold text-slate-200">MIME_LEN</span>
            <span className="text-[9px] text-slate-400 block mt-1">uint16</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[10px] text-slate-500 block">2 BYTES</span>
            <span className="text-xs font-bold text-slate-200">FN_LEN</span>
            <span className="text-[9px] text-slate-400 block mt-1">uint16</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-pink-800/60">
            <span className="text-[10px] text-slate-500 block">4 BYTES</span>
            <span className="text-xs font-bold text-pink-300">PAYLOAD_LEN</span>
            <span className="text-[9px] text-slate-400 block mt-1">uint32</span>
          </div>
        </div>

        <ul className="space-y-2 text-xs text-slate-300">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span><strong>Protection against OOM & DoS:</strong> Header lengths are validated before memory buffer allocation.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span><strong>CRC32 Pre-Decryption Verification:</strong> Detects if carrier media was clipped or converted before initiating expensive cryptographic computations.</span>
          </li>
        </ul>
      </div>

      {/* 4. Video Steganography & Codec Preservation */}
      <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-pink-950/80 border border-pink-800/50 flex items-center justify-center text-pink-400">
            <Video className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">4. Video Steganography: The Codec Compression Dilemma</h3>
            <p className="text-xs text-slate-400 font-mono">Why naive video steganography fails and how we solve it</p>
          </div>
        </div>

        <div className="space-y-4 text-xs text-slate-300 leading-relaxed">
          <p>
            In standard video compression (like standard H.264, VP9, or AV1), video encoders apply 
            <strong> lossy Discrete Cosine Transform (DCT)</strong> quantization and chroma subsampling (YUV 4:2:0). 
            This process intentionally rounds high-frequency spatial details—which completely flips pixel LSBs and ruins 
            conventional steganography!
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/40 space-y-2">
              <span className="font-bold text-rose-400 text-xs flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4" />
                Standard Lossy Codec (Fails)
              </span>
              <p className="text-xs text-slate-400">
                DCT quantization and YUV chroma rounding alters pixel values: <code>RGB(124, 85, 201)</code> becomes 
                <code>RGB(125, 84, 200)</code>. LSB bits are destroyed and recovery fails.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40 space-y-2">
              <span className="font-bold text-emerald-400 text-xs flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                Our Lossless FFmpeg Pipeline (100% Exact)
              </span>
              <p className="text-xs text-slate-400">
                We pipe raw BGR frames to FFmpeg with <code>libx264rgb -crf 0 -preset ultrafast</code>. 
                This preserves true mathematical pixel values with 0 bit errors and preserves audio tracks.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
