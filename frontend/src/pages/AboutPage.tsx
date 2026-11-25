import React from 'react';
import { Activity, ShieldCheck, Cpu, Layers, AlertTriangle, BookOpen, CheckCircle } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16 text-slate-800 dark:text-slate-200">
      {/* Title */}
      <div className="space-y-2 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full text-xs font-mono bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20 font-semibold">
          <Activity className="w-3.5 h-3.5" />
          <span>Energy & Utilities • Image Restoration & Enhancement</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">
          InfraClarity AI: Infrastructure Inspection Image Enhancer
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Restoring degraded drone and telephoto optical imagery of power transmission towers, pipelines, and utility corridors.
        </p>
      </div>

      {/* Purpose Section */}
      <section className="space-y-3">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-brand-500" />
          <span>Mission & Engineering Purpose</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          Utility maintenance teams routinely inspect high-voltage transmission towers, sub-stations, and pipeline networks using drones. Images captured at safe standoff distances or in adverse weather often suffer from atmospheric haze, rain scattering, low lighting, telephoto motion blur, and sensor shot noise.
        </p>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          InfraClarity AI diagnoses optical degradations with mathematical rigor and applies a sequenced, memory-safe restoration pipeline so that critical structural faults—hairline weld cracks, rust pitting, loose bolt threads, and chipped glass insulators—become clearly visible to inspection engineers.
        </p>
      </section>

      {/* Degradation Metrics & Formulas */}
      <section className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-brand-500" />
          <span>Degradation Analysis Metrics</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5">
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400 font-mono">1. Blur Score</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Variance of the Laplacian operator on grayscale luminance:
            </p>
            <div className="bg-slate-100 dark:bg-slate-850 p-2 rounded text-[11px] font-mono text-slate-800 dark:text-slate-200">
              Score = Var(∇² I) = (1/N) ∑ (L(x,y) - μ_L)²
            </div>
            <p className="text-[11px] text-slate-500">
              Sharp defect boundaries produce high second derivatives; blurred imagery yields low variance.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5">
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400 font-mono">2. Haze Score</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Mean of Dark Channel Prior over 15×15 local sliding patches:
            </p>
            <div className="bg-slate-100 dark:bg-slate-850 p-2 rounded text-[11px] font-mono text-slate-800 dark:text-slate-200">
              J_dark(x) = min_(y ∈ Ω(x)) (min_(c ∈ RGB) I^c(y))
            </div>
            <p className="text-[11px] text-slate-500">
              In clear outdoor scenes dark channels approach zero; atmospheric scattering adds airlight.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5">
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400 font-mono">3. Noise Estimate</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Robust standard deviation estimate from high-frequency wavelet residuals (MAD estimator):
            </p>
            <div className="bg-slate-100 dark:bg-slate-850 p-2 rounded text-[11px] font-mono text-slate-800 dark:text-slate-200">
              σ_hat = Median(|detail_coeffs|) / 0.6745
            </div>
            <p className="text-[11px] text-slate-500">
              Measures sensor noise floor while remaining robust against sharp structural edges.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1.5">
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400 font-mono">4. RMS Contrast</span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Root-Mean-Square contrast of normalized luminance:
            </p>
            <div className="bg-slate-100 dark:bg-slate-850 p-2 rounded text-[11px] font-mono text-slate-800 dark:text-slate-200">
              RMS = √((1/N) ∑ (I(x,y) - μ_I)²)
            </div>
            <p className="text-[11px] text-slate-500">
              Identifies washed-out overcast frames or low-light underexposed shadow areas.
            </p>
          </div>
        </div>
      </section>

      {/* Memory-Safe Tiling */}
      <section className="space-y-3">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider flex items-center space-x-2">
          <Layers className="w-4 h-4 text-brand-500" />
          <span>Tiled Inference Architecture</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          High-resolution drone payloads often produce 24MP+ images (up to 6000×4000). To ensure smooth execution on standard field laptops with no dedicated GPU, InfraClarity AI tiles images into 512×512 blocks with 32px overlap. Reassembly uses 2D cosine-feathered blending:
        </p>
        <div className="bg-slate-100 dark:bg-slate-850 p-3 rounded-lg text-xs font-mono text-slate-800 dark:text-slate-200">
          I_out = (∑ w_i · T_i) / (∑ w_i)
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          This formulation mathematically guarantees exact identity reconstruction within 1 intensity level (1/255) and prevents visible seam lines or tiling boundary artifacts.
        </p>
      </section>

      {/* Honest Limitations Notice */}
      <section className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 p-5 rounded-xl space-y-2 text-xs text-amber-900 dark:text-amber-200">
        <div className="flex items-center space-x-2 font-bold text-amber-800 dark:text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
          <span>Operational Limitations & Human Review Mandate</span>
        </div>
        <p className="leading-relaxed">
          InfraClarity AI is an optical image restoration and enhancement tool, <strong>not an automated defect classification or structural pass/fail certification system</strong>.
        </p>
        <ul className="list-disc list-inside space-y-1 text-amber-800 dark:text-amber-300/90 pl-1">
          <li>Restoration and super-resolution techniques boost edge contrast and can occasionally hallucinate subtle sub-pixel texture. All enhanced images must be reviewed by qualified structural inspection personnel.</li>
          <li>Edge density and detail gain metrics are proxies for visual fault contrast, not certified crack depth or material loss measurements.</li>
          <li>Always retain original unaltered RAW/JPEG inspection files for legal utility compliance and compliance archives (ASME, IEEE, NERC).</li>
        </ul>
      </section>
    </div>
  );
};
