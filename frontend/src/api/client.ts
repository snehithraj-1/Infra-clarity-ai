import { Capabilities, DegradationReport, EnhanceOptions, JobStatus } from '../types';

const API_BASE = '/api/v1';

export function formatApiError(err: any): string {
  const msg = err?.message || '';
  if (msg.includes('Failed to fetch') || err?.name === 'TypeError') {
    return 'Backend offline: Cannot connect to FastAPI server at http://127.0.0.1:8000. Please start it using "npm run dev".';
  }
  return msg || 'Unexpected network error';
}

export async function fetchCapabilities(): Promise<Capabilities> {
  const res = await fetch(`${API_BASE}/capabilities`);
  if (!res.ok) {
    throw new Error(`Failed to fetch capabilities: ${res.statusText}`);
  }
  return res.json();
}

export interface InspectionSample {
  id: string;
  title: string;
  asset_type: string;
  degradation: string;
  description: string;
  filename: string;
}

export async function fetchInspectionSamples(): Promise<InspectionSample[]> {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) {
    throw new Error(`Failed to fetch samples: ${res.statusText}`);
  }
  return res.json();
}

export function getSampleImageUrl(sampleId: string): string {
  return `${API_BASE}/samples/${sampleId}/image`;
}

export async function analyzeImage(file: File): Promise<DegradationReport> {
  const formData = new FormData();
  formData.append('image', file);

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Analysis failed with status ${res.status}`);
  }
  return res.json();
}

export async function submitEnhanceJob(
  file: File,
  options: EnhanceOptions
): Promise<{ job_id: string; status: string }> {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('options', JSON.stringify(options));

  const res = await fetch(`${API_BASE}/enhance`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Enhancement submission failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error(`Failed to load job ${jobId}`);
  }
  return res.json();
}

export function subscribeJobEvents(
  jobId: string,
  onProgress: (status: JobStatus) => void,
  onError?: (error: Error) => void
): () => void {
  const eventSource = new EventSource(`${API_BASE}/jobs/${jobId}/events`);

  eventSource.addEventListener('progress', (e) => {
    try {
      const data: JobStatus = JSON.parse(e.data);
      onProgress(data);
      if (data.status === 'completed' || data.status === 'failed') {
        eventSource.close();
      }
    } catch (err) {
      console.error('Error parsing SSE progress event', err);
    }
  });

  eventSource.onerror = (e) => {
    console.warn('SSE connection issue, falling back or reconnecting...', e);
    if (onError) {
      onError(new Error('Event stream encountered a connection error.'));
    }
  };

  return () => {
    eventSource.close();
  };
}

export function getResultImageUrl(jobId: string, format?: string, quality?: number, matchOriginal?: boolean): string {
  const params = new URLSearchParams();
  if (format) params.set('format', format);
  if (quality) params.set('quality', quality.toString());
  if (matchOriginal) params.set('match_original', 'true');
  const qs = params.toString();
  return `${API_BASE}/jobs/${jobId}/result${qs ? `?${qs}` : ''}`;
}

export function getOriginalImageUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/original`;
}

export interface AssistantResponse {
  reply: string;
  suggested_prompts: string[];
  asset_type: string;
  risk_level: string;
  engine?: string;
}

export async function askAssistant(
  message: string,
  context?: {
    job_id?: string | null;
    report?: DegradationReport | null;
    metrics?: any;
    stages?: any[];
    history?: { role: string; content: string }[];
    api_key?: string | null;
  }
): Promise<AssistantResponse> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (context?.api_key) {
    headers['X-Gemini-Key'] = context.api_key;
  }

  const res = await fetch(`${API_BASE}/assistant/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      message,
      job_id: context?.job_id || null,
      report: context?.report || null,
      metrics: context?.metrics || null,
      stages: context?.stages || null,
      history: context?.history || [],
      api_key: context?.api_key || null,
    }),
  });

  if (!res.ok) {
    throw new Error(`Assistant request failed: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Real-time SSE streaming assistant client.
 * Receives tokens chunk-by-chunk for sub-second latency and smooth Gemini typing output.
 */
export async function streamAssistant(
  message: string,
  context: {
    job_id?: string | null;
    report?: DegradationReport | null;
    metrics?: any;
    stages?: any[];
    history?: { role: string; content: string }[];
    api_key?: string | null;
  },
  onChunk: (accumulatedText: string, meta?: Partial<AssistantResponse>) => void,
  onComplete: (res: AssistantResponse) => void,
  onError: (err: Error) => void
): Promise<void> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (context?.api_key) {
    headers['X-Gemini-Key'] = context.api_key;
  }

  try {
    const res = await fetch(`${API_BASE}/assistant/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message,
        job_id: context?.job_id || null,
        report: context?.report || null,
        metrics: context?.metrics || null,
        stages: context?.stages || null,
        history: context?.history || [],
        api_key: context?.api_key || null,
      }),
    });

    if (!res.ok || !res.body) {
      throw new Error(`Streaming failed: ${res.statusText || 'No response body'}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let accumulatedText = '';
    let finalMeta: Partial<AssistantResponse> = {};

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const data = JSON.parse(trimmed.slice(6));
            if (data.chunk) {
              accumulatedText += data.chunk;
              onChunk(accumulatedText, data);
            }
            if (data.done) {
              finalMeta = {
                asset_type: data.asset_type,
                risk_level: data.risk_level,
                engine: data.engine,
                suggested_prompts: data.suggested_prompts,
              };
            }
          } catch (e) {
            // Ignore partial chunk JSON parse errors
          }
        }
      }
    }

    onComplete({
      reply: accumulatedText,
      suggested_prompts: finalMeta.suggested_prompts || [
        'Tell me what is in this image',
        'What loopholes and blindspots exist in the raw capture?',
        'Are there cracks or corrosion near the bolts?',
        'Generate formal asset inspection report',
      ],
      asset_type: finalMeta.asset_type || 'Infrastructure Inspection Asset',
      risk_level: finalMeta.risk_level || 'Medium',
      engine: finalMeta.engine || 'gemini-live',
    });
  } catch (err: any) {
    console.warn('Assistant streaming issue, falling back to standard chat:', err);
    try {
      const fallback = await askAssistant(message, context);
      onChunk(fallback.reply, fallback);
      onComplete(fallback);
    } catch (fallbackErr: any) {
      onError(fallbackErr);
    }
  }
}
