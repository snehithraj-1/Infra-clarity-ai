import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  Key,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Zap,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
} from 'lucide-react';
import { useEnhanceStore } from '../../store/useEnhanceStore';
import { askAssistant, streamAssistant, AssistantResponse } from '../../api/client';
import { MarkdownRenderer } from '../common/MarkdownRenderer';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  assetType?: string;
  riskLevel?: string;
  engine?: string;
  isStreaming?: boolean;
}

export const InspectionAssistant: React.FC = () => {
  const { report, jobStatus, jobId } = useEnhanceStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [apiKey, setApiKey] = useState<string>(() => {
    return (
      localStorage.getItem('infraclarity_gemini_key') || ''
    );
  });
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([
    'Tell me what is in this image',
    'Identify loopholes & vulnerabilities in original image',
    'Why is the enhanced image so clear now?',
    'Check insulator shed integrity and flashovers',
  ]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [speakingMsgId, setSpeakingMsgId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const handleSpeakMessage = (id: string, text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      return;
    }
    if (speakingMsgId === id) {
      window.speechSynthesis.cancel();
      setSpeakingMsgId(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanText = text
      .replace(/[#*`_~\[\]]/g, '')
      .replace(/<[^>]*>/g, '')
      .replace(/\|/g, ' ')
      .trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.onend = () => setSpeakingMsgId(null);
    utterance.onerror = () => setSpeakingMsgId(null);
    setSpeakingMsgId(id);
    window.speechSynthesis.speak(utterance);
  };

  const handleToggleVoice = () => {
    if (typeof window === 'undefined') return;
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Voice dictation is not supported in this browser. Please use Chrome/Edge.');
      return;
    }
    if (isListening) {
      setIsListening(false);
      return;
    }
    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInput(transcript);
          handleSendMessage(transcript);
        }
        setIsListening(false);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognition.start();
    } catch (err) {
      setIsListening(false);
    }
  };

  // Save API key to localStorage when updated
  const handleSaveApiKey = (key: string) => {
    setApiKey(key);
    localStorage.setItem('infraclarity_gemini_key', key.trim());
  };

  // Initial greeting / analysis overview once report or metrics are loaded
  useEffect(() => {
    if (!report && !jobStatus?.metrics) return;
    if (messages.length > 0) return;

    const fetchInitialReport = async () => {
      const initId = 'init-1';
      setMessages([
        {
          id: initId,
          sender: 'assistant',
          text: '',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isStreaming: true,
          engine: apiKey ? 'gemini-flash-lite' : 'expert-heuristic',
        },
      ]);
      setIsLoading(false);

      await streamAssistant(
        'Initial inspection diagnosis overview',
        {
          job_id: jobId,
          report: report,
          metrics: jobStatus?.metrics,
          stages: jobStatus?.stages,
          api_key: apiKey || null,
        },
        (chunkText, meta) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === initId
                ? {
                    ...m,
                    text: chunkText,
                    assetType: meta?.asset_type || m.assetType,
                    riskLevel: meta?.risk_level || m.riskLevel,
                    engine: meta?.engine || m.engine,
                    isStreaming: true,
                  }
                : m
            )
          );
        },
        (res) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === initId
                ? {
                    ...m,
                    text: res.reply || m.text,
                    assetType: res.asset_type,
                    riskLevel: res.risk_level,
                    engine: res.engine,
                    isStreaming: false,
                  }
                : m
            )
          );
          if (res.suggested_prompts && res.suggested_prompts.length > 0) {
            setSuggestedPrompts(res.suggested_prompts);
          }
        },
        (err) => {
          console.warn('Initial assistant stream fallback:', err);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === initId
                ? {
                    ...m,
                    text: '⚠️ Initial diagnosis overview unavailable. Ask any question in plain words below.',
                    isStreaming: false,
                  }
                : m
            )
          );
        }
      );
    };

    fetchInitialReport();
  }, [report, jobStatus?.metrics, jobId]);

  useEffect(() => {
    // Scroll internally inside the chat container only when multiple messages exist; never scroll the outer browser window!
    if (messages.length > 2 && chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages.length, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const q = (textToSend || input).trim();
    if (!q || isLoading) return;

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const astId = `ast-${Date.now() + 1}`;
    const initialAssistantMsg: ChatMessage = {
      id: astId,
      sender: 'assistant',
      text: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isStreaming: true,
      engine: apiKey ? 'gemini-flash-lite' : 'expert-heuristic',
    };

    const updatedHistory = [...messages, userMsg];
    setMessages([...updatedHistory, initialAssistantMsg]);
    setInput('');
    setIsLoading(false);

    try {
      const historyPayload = updatedHistory.slice(-6).map((m) => ({
        role: m.sender,
        content: m.text,
      }));

      await streamAssistant(
        q,
        {
          job_id: jobId,
          report: report,
          metrics: jobStatus?.metrics,
          stages: jobStatus?.stages,
          history: historyPayload,
          api_key: apiKey || null,
        },
        (accumulatedText, meta) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === astId
                ? {
                    ...m,
                    text: accumulatedText,
                    assetType: meta?.asset_type || m.assetType,
                    riskLevel: meta?.risk_level || m.riskLevel,
                    engine: meta?.engine || m.engine,
                    isStreaming: true,
                  }
                : m
            )
          );
        },
        (res) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === astId
                ? {
                    ...m,
                    text: res.reply || m.text,
                    assetType: res.asset_type,
                    riskLevel: res.risk_level,
                    engine: res.engine,
                    isStreaming: false,
                  }
                : m
            )
          );
          if (res.suggested_prompts && res.suggested_prompts.length > 0) {
            setSuggestedPrompts(res.suggested_prompts);
          }
        },
        (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === astId
                ? {
                    ...m,
                    text: `⚠️ **Inspection Assistant Alert**: Unable to connect to diagnostic engine (${err.message || 'Network issue'}). Please retry.`,
                    isStreaming: false,
                  }
                : m
            )
          );
        }
      );
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === astId
            ? {
                ...m,
                text: `⚠️ **Inspection Assistant Alert**: Unable to connect to diagnostic engine (${err.message || 'Network issue'}). Please retry.`,
                isStreaming: false,
              }
            : m
        )
      );
    }
  };

  const handleResetChat = () => {
    setMessages([]);
    setSuggestedPrompts([
      'Analyze critical faults and risks in this image',
      'Check insulator shed integrity and flashovers',
      'Evaluate corrosion severity and weld condition',
      'Explain in simple words what was fixed',
    ]);
  };

  const handleCopyMessage = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="cyber-panel rounded-2xl shadow-2xl overflow-hidden transition-all duration-200">
      {/* Assistant Header */}
      <div className="px-5 py-4 bg-slate-950/95 border-b border-slate-800 text-white flex items-center justify-between select-none">
        <div
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-3 cursor-pointer flex-1"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 to-cyan-500/10 border border-amber-500/40 flex items-center justify-center text-amber-400 shadow-md glow-amber">
            <Bot className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold tracking-tight text-white font-mono">
                TACTICAL INSPECTION COPILOT
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 font-bold flex items-center space-x-1">
                <Zap className="w-2.5 h-2.5" />
                <span>ACTIVE</span>
              </span>
              {apiKey && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold flex items-center space-x-1">
                  <Sparkles className="w-2.5 h-2.5" />
                  <span>GEMINI CONNECTED</span>
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Natural language asset recognition, defect diagnosis, and blindspot auditing
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* API Key Configure Button */}
          <button
            type="button"
            onClick={() => setShowKeyModal(!showKeyModal)}
            title="Configure Gemini API Key"
            className={`px-2.5 py-1.5 rounded-xl border text-xs font-mono transition-colors flex items-center space-x-1.5 ${
              apiKey
                ? 'border-cyan-500/40 bg-cyan-950/40 text-cyan-300 hover:bg-cyan-900/40'
                : 'border-slate-800 bg-slate-900 text-slate-400 hover:text-white'
            }`}
          >
            <Key className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[10px] hidden sm:inline">
              {apiKey ? 'API KEY ACTIVE' : 'SET KEY'}
            </span>
          </button>

          {/* Reset Chat Button */}
          {messages.length > 0 && (
            <button
              type="button"
              onClick={handleResetChat}
              title="Reset conversation"
              className="p-1.5 rounded-xl border border-slate-800 bg-slate-900 text-slate-400 hover:text-amber-400 hover:border-slate-700 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-900"
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Optional Gemini Key Input Drawer */}
      {showKeyModal && (
        <div className="px-5 py-3 bg-slate-950/90 border-b border-slate-800 text-xs flex flex-col sm:flex-row items-center gap-2">
          <div className="flex items-center space-x-2 flex-1 text-slate-300">
            <Key className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <span>Optional Gemini API Key:</span>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => handleSaveApiKey(e.target.value)}
              placeholder="Enter Gemini API key (leave blank to use built-in expert engine)"
              className="flex-1 text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
            />
          </div>
          <div className="text-[10px] text-slate-400 flex-shrink-0">
            {apiKey ? '✓ Connected to Gemini Live' : '⚡ Using Built-in Utility Engine'}
          </div>
        </div>
      )}

      {/* Expandable Assistant Body */}
      {isExpanded && (
        <div className="flex flex-col h-[480px]">
          {/* Quick Prompt Pills */}
          <div className="px-4 py-2.5 bg-slate-950/80 border-b border-slate-800 flex items-center gap-2 overflow-x-auto no-scrollbar">
            <span className="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider flex-shrink-0">
              PROMPT PILLS:
            </span>
            {suggestedPrompts.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSendMessage(prompt)}
                disabled={isLoading}
                className="text-[11px] font-mono font-medium px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 hover:border-amber-400 hover:text-amber-300 hover:bg-slate-800/80 whitespace-nowrap transition-all flex-shrink-0 disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Conversation Stream */}
          <div ref={chatContainerRef} className="flex-1 p-4 overflow-y-auto space-y-4 text-xs font-sans bg-slate-950/50">
            {messages.length === 0 && !isLoading && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-2">
                <Sparkles className="w-8 h-8 text-amber-400/50" />
                <p className="font-semibold text-slate-200 font-mono">
                  InfraClarity Tactical Copilot Standing By
                </p>
                <p className="text-[11px] max-w-sm text-slate-400">
                  Ask any question in plain words — e.g. "Tell me what is in this image", "Are the bolts corroded?", "Why did it blur?", or "Explain in simple terms".
                </p>
              </div>
            )}

            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${
                  m.sender === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`max-w-[88%] rounded-2xl px-4 py-3 shadow-lg ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold rounded-br-none shadow-md glow-amber'
                      : 'bg-slate-900/90 text-slate-100 border border-slate-800/90 rounded-bl-none shadow-xl'
                  }`}
                >
                  {/* Assistant Message Header Badges */}
                  {m.sender === 'assistant' && (
                    <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-200 dark:border-slate-700/60 text-[10px] text-slate-500 dark:text-slate-400">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-brand-600 dark:text-brand-400">
                          {m.assetType || 'Utility Asset'}
                        </span>
                        {m.riskLevel && (
                          <span
                            className={`px-1.5 py-0.5 rounded font-mono font-bold uppercase text-[9px] ${
                              m.riskLevel === 'Critical'
                                ? 'bg-rose-500/20 text-rose-500 border border-rose-500/30'
                                : m.riskLevel === 'High'
                                ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30'
                                : 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
                            }`}
                          >
                            {m.riskLevel} Risk
                          </span>
                        )}
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-bold flex items-center space-x-1">
                          <Sparkles className="w-2.5 h-2.5 text-cyan-400" />
                          <span>{m.engine?.includes('gemini') ? '✨ Gemini Multimodal AI' : '⚡ Tactical Copilot'}</span>
                        </span>
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <button
                          type="button"
                          onClick={() => handleSpeakMessage(m.id, m.text)}
                          className="hover:text-slate-800 dark:hover:text-white transition-colors"
                          title={speakingMsgId === m.id ? 'Stop audio' : 'Audio briefing (Read aloud)'}
                        >
                          {speakingMsgId === m.id ? (
                            <VolumeX className="w-3.5 h-3.5 text-brand-500 animate-pulse" />
                          ) : (
                            <Volume2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleCopyMessage(m.id, m.text)}
                          className="hover:text-slate-800 dark:hover:text-white transition-colors flex items-center space-x-1"
                          title="Copy to clipboard"
                        >
                          {copiedId === m.id ? (
                            <Check className="w-3 h-3 text-emerald-500" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Message Content rendered with rich Gemini formatting */}
                  <div className="leading-relaxed font-sans">
                    {m.sender === 'user' ? (
                      <div className="text-xs font-semibold leading-relaxed font-sans">{m.text}</div>
                    ) : (
                      <MarkdownRenderer content={m.text} isStreaming={m.isStreaming} />
                    )}
                  </div>

                  <div
                    className={`mt-1.5 text-[9px] ${
                      m.sender === 'user' ? 'text-slate-800/70' : 'text-slate-400'
                    } text-right`}
                  >
                    {m.timestamp}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center space-x-2 text-slate-500 text-xs pl-2">
                <div className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
                <span className="font-mono text-[11px]">Formulating engineering response to your query...</span>
              </div>
            )}
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-slate-50 dark:bg-slate-950/70 border-t border-slate-200 dark:border-slate-800 flex items-center space-x-2"
          >
            <button
              type="button"
              onClick={handleToggleVoice}
              title={isListening ? 'Listening... click to stop' : 'Voice input (Speak query)'}
              className={`p-2.5 rounded-xl border transition-colors flex items-center justify-center flex-shrink-0 ${
                isListening
                  ? 'bg-rose-500 text-white border-rose-600 animate-pulse'
                  : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:text-brand-500'
              }`}
            >
              {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isListening ? 'Listening to voice query...' : "Ask anything in your words (e.g. 'Is that rust bad?', 'Are bolts loose?')..."}
              disabled={isLoading}
              className="flex-1 text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 shadow-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Ask</span>
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
