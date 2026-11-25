import React from 'react';

interface MarkdownRendererProps {
  content: string;
  isStreaming?: boolean;
}

/**
 * Parses inline markdown: **bold**, `code`, *italic*, and [links](url).
 */
function renderInline(text: string): React.ReactNode[] {
  const elements: React.ReactNode[] = [];
  // Tokenize regex for inline markdown
  const tokenRegex = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = tokenRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      elements.push(text.substring(lastIndex, match.index));
    }

    const token = match[0];
    const key = `${match.index}-${token.slice(0, 10)}`;

    if (token.startsWith('**') && token.endsWith('**')) {
      elements.push(
        <strong key={key} className="font-bold text-white tracking-wide">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      elements.push(
        <code
          key={key}
          className="px-1.5 py-0.5 mx-0.5 rounded-md bg-slate-800/90 border border-slate-700/60 text-cyan-300 font-mono text-[11px]"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      elements.push(
        <em key={key} className="italic text-slate-300">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith('[') && token.includes('](') && token.endsWith(')')) {
      const parts = token.slice(1, -1).split('](');
      elements.push(
        <a
          key={key}
          href={parts[1]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-amber-400 underline hover:text-amber-300"
        >
          {parts[0]}
        </a>
      );
    } else {
      elements.push(token);
    }

    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    elements.push(text.substring(lastIndex));
  }

  return elements.length > 0 ? elements : [text];
}

/**
 * Ultra-responsive, Gemini-styled rich Markdown renderer with full table, blockquote,
 * heading, and list item support, featuring real-time pulsing typing cursor.
 */
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, isStreaming }) => {
  if (!content) return null;

  const lines = content.split('\n');
  const renderedBlocks: React.ReactNode[] = [];
  let tableRows: string[] = [];
  let listItems: string[] = [];

  const flushTable = (keyPrefix: number) => {
    if (tableRows.length === 0) return;
    const headerRow = tableRows[0];
    const isDivider = (r: string) => /^[|\s-:]+$/.test(r);
    const dataRows = tableRows.slice(1).filter((r) => !isDivider(r));

    const parseCells = (rowStr: string) =>
      rowStr
        .split('|')
        .slice(1, -1)
        .map((c) => c.trim());

    const headers = parseCells(headerRow);

    renderedBlocks.push(
      <div key={`table-${keyPrefix}`} className="overflow-x-auto my-3 rounded-xl border border-slate-800 shadow-md">
        <table className="min-w-full text-xs font-sans border-collapse bg-slate-900/70">
          <thead>
            <tr className="bg-slate-950/90 border-b border-slate-800 text-slate-300">
              {headers.map((h, i) => (
                <th key={i} className="px-3 py-2 text-left font-mono font-bold text-amber-400 uppercase tracking-wider text-[10px]">
                  {renderInline(h)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {dataRows.map((r, ri) => (
              <tr key={ri} className="hover:bg-slate-800/30 transition-colors">
                {parseCells(r).map((cell, ci) => (
                  <td key={ci} className="px-3 py-2 text-slate-200">
                    {renderInline(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    tableRows = [];
  };

  const flushList = (keyPrefix: number) => {
    if (listItems.length === 0) return;
    renderedBlocks.push(
      <ul key={`list-${keyPrefix}`} className="space-y-1.5 my-2 pl-1">
        {listItems.map((item, i) => {
          // Check for bold title format: **Title:** Content
          const boldMatch = item.match(/^\*\*([^*]+)\*\*:(.*)$/);
          if (boldMatch) {
            return (
              <li key={i} className="flex items-start space-x-2 text-xs leading-relaxed text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0 glow-amber" />
                <div>
                  <span className="font-bold text-white mr-1.5 bg-slate-800/50 px-1 py-0.5 rounded text-[11px] font-mono border border-slate-700/40">
                    {boldMatch[1]}:
                  </span>
                  <span>{renderInline(boldMatch[2].trim())}</span>
                </div>
              </li>
            );
          }

          return (
            <li key={i} className="flex items-start space-x-2 text-xs leading-relaxed text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
              <span>{renderInline(item)}</span>
            </li>
          );
        })}
      </ul>
    );
    listItems = [];
  };

  for (let idx = 0; idx < lines.length; idx++) {
    const rawLine = lines[idx];
    const line = rawLine.trim();

    // Check table rows
    if (line.startsWith('|') && line.endsWith('|')) {
      flushList(idx);
      tableRows.push(line);
      continue;
    } else if (tableRows.length > 0) {
      flushTable(idx);
    }

    // Check list items (* or -)
    const bulletMatch = line.match(/^[*•-]\s+(.*)$/);
    const numberedMatch = line.match(/^\d+\.\s+(.*)$/);
    if (bulletMatch || numberedMatch) {
      const itemText = bulletMatch ? bulletMatch[1] : numberedMatch![1];
      listItems.push(itemText);
      continue;
    } else if (listItems.length > 0) {
      flushList(idx);
    }

    // Headings
    if (line.startsWith('### ')) {
      const headingText = line.slice(4).trim();
      renderedBlocks.push(
        <div key={`h3-${idx}`} className="mt-3.5 mb-2 pt-2 border-t border-slate-800/80 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-sm bg-amber-400 rotate-45 flex-shrink-0" />
          <h4 className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider">
            {renderInline(headingText)}
          </h4>
        </div>
      );
      continue;
    }

    if (line.startsWith('## ')) {
      const headingText = line.slice(3).trim();
      renderedBlocks.push(
        <div key={`h2-${idx}`} className="mt-4 mb-2 pt-2 border-t border-slate-800 flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded bg-cyan-400 flex-shrink-0" />
          <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
            {renderInline(headingText)}
          </h3>
        </div>
      );
      continue;
    }

    if (line.startsWith('# ')) {
      const headingText = line.slice(2).trim();
      renderedBlocks.push(
        <h2 key={`h1-${idx}`} className="text-base font-bold text-white font-mono mt-4 mb-2">
          {renderInline(headingText)}
        </h2>
      );
      continue;
    }

    // Blockquotes (> ...)
    if (line.startsWith('>')) {
      const quoteText = line.slice(1).trim();
      renderedBlocks.push(
        <div
          key={`quote-${idx}`}
          className="my-2.5 p-3 rounded-xl bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-2 border-amber-400 text-amber-200 text-xs shadow-inner"
        >
          {renderInline(quoteText)}
        </div>
      );
      continue;
    }

    // Horizontal Rule
    if (line === '---' || line === '***' || line === '___') {
      renderedBlocks.push(<hr key={`hr-${idx}`} className="my-3 border-slate-800" />);
      continue;
    }

    // Normal paragraph
    if (line.length > 0) {
      renderedBlocks.push(
        <p key={`p-${idx}`} className="my-1.5 text-xs text-slate-200 leading-relaxed font-sans">
          {renderInline(line)}
        </p>
      );
    }
  }

  // Flush remaining buffers
  if (tableRows.length > 0) flushTable(lines.length);
  if (listItems.length > 0) flushList(lines.length);

  return (
    <div className="space-y-1 font-sans">
      {renderedBlocks}
      {isStreaming && (
        <span className="inline-block w-2 h-3.5 bg-amber-400 animate-pulse ml-1 align-middle rounded-sm shadow-sm glow-amber" />
      )}
    </div>
  );
};

